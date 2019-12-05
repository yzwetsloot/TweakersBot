import json
import logging.config
import random
import re
import time

from bs4 import BeautifulSoup, SoupStrainer
import requests
import yaml

from notification import price_notification
from pricedifference import calculate_price_difference
from requestcookies import get_cookies
from proxy import filter_proxies, retrieve_proxies

with open("../config/log.yaml") as config:
    parameters = yaml.safe_load(config.read())
    logging.config.dictConfig(parameters)

logger = logging.getLogger(__name__)

link_tags = SoupStrainer('a')

price_pattern = re.compile("\\s*€ [0-9.]+,(-|[0-9]+)\\s*")
pricewatch_pattern = re.compile("^€ [0-9.]+,(-|[0-9]+)$")
sellers_pattern = re.compile(".*pricewatch/.*/aanbod/\s*")
recaptcha_pattern = re.compile(".*Captcha.*")

with open("../config/config.json") as config:
    parameters = json.load(config)

START_PAGE = parameters["start_page"]
BATCH_SIZE = parameters["batch_size"]
TIMEOUT = parameters["timeout"]
CYCLE_RANGE = parameters["cycle_range"]
PRODUCT_RANGE = parameters["product_range"]
HEADERS = parameters["headers"]


def parse_float(price: str) -> float:
    return float(re.sub("€|\\s|-|\\.", '', price).replace(",", "."))


def main() -> None:
    endpoints = open("../resources/endpoints.txt").read().splitlines()
    proxies = filter_proxies(retrieve_proxies(endpoints), START_PAGE, 2.5, 2.0)

    proxy = proxies[random.randrange(0, len(proxies) - 1)]
    logger.info(f"Retrieved {len(proxies)} proxies; using proxy {proxy}")

    visited = []
    cookies = get_cookies(proxy)

    while True:
        candidates = []

        while True:
            try:
                response = requests.get(START_PAGE, headers=HEADERS, cookies=cookies, proxies={"https": proxy})
                break
            except requests.RequestException:
                proxies.remove(proxy)
                proxy = proxies[random.randrange(0, len(proxies) - 1)]
                logger.error(f"Connection error occurred; switch to {proxy}")
                time.sleep(TIMEOUT)

        soup = BeautifulSoup(response.content, "lxml", parse_only=link_tags)

        products = [{"url": product["href"].strip(), "current_price": parse_float(product.string)}
                    for product in soup.find_all('a', string=price_pattern)]

        for product in products[:BATCH_SIZE]:
            if product["url"] not in visited:
                while True:
                    try:
                        response = requests.get(product["url"], headers=HEADERS, cookies=cookies, proxies={"https": proxy})
                        break
                    except requests.RequestException:
                        proxies.remove(proxy)
                        proxy = proxies[random.randrange(0, len(proxies) - 1)]
                        logger.error(f"Connection error occurred; switch to {proxy}")
                        time.sleep(TIMEOUT)

                soup = BeautifulSoup(response.content, "lxml", parse_only=link_tags)
                pricewatch_page = soup.find(class_=["thumb normal", "thumb normal empty"])

                if pricewatch_page:
                    count = 0
                    while True:
                        try:
                            response = requests.get(pricewatch_page["href"], headers=HEADERS, cookies=cookies, proxies={"https": proxy})
                        except requests.RequestException:
                            proxies.remove(proxy)
                            proxy = proxies[random.randrange(0, len(proxies) - 1)]
                            logger.error(f"Connection error occurred; switch to {proxy}")
                            time.sleep(TIMEOUT)
                            continue

                        soup = BeautifulSoup(response.content, "lxml")

                        if soup.find(string=recaptcha_pattern):
                            logger.info(f"ReCaptcha presented; retrieve cookies")
                            proxy = proxies[random.randrange(0, len(proxies) - 1)]
                            cookies = get_cookies(proxy)
                            # time.sleep(random.randrange(CYCLE_RANGE[0] * 2 ** count, CYCLE_RANGE[1] * 2 ** count))
                            count += 1
                            continue
                        break

                    pricewatch_price = soup.find(string=pricewatch_pattern)
                    product["new_price"] = parse_float(pricewatch_price.string) if pricewatch_price else None

                    sellers_page = soup.find(href=sellers_pattern)

                    if sellers_page:
                        count = 0
                        while True:
                            try:
                                response = requests.get(sellers_page["href"], headers=HEADERS, cookies=cookies, proxies={"https": proxy})
                            except requests.RequestException:
                                proxies.remove(proxy)
                                proxy = proxies[random.randrange(0, len(proxies) - 1)]
                                logger.error(f"Connection error occurred; switch to {proxy}")
                                time.sleep(TIMEOUT)
                                continue

                            soup = BeautifulSoup(response.content, "lxml")

                            if soup.find(string=recaptcha_pattern):
                                # TODO resolve cookie-issue
                                # Try adjusting user agent
                                # Increase timeout on retry
                                proxy = proxies[random.randrange(0, len(proxies) - 1)]
                                cookies = get_cookies(proxy)
                                logger.info(f"ReCaptcha presented; retrieve cookies")
                                # time.sleep(random.randrange(CYCLE_RANGE[0] * 2 ** count, CYCLE_RANGE[1] * 2 ** count))
                                count += 1
                                continue
                            break

                        product["other_prices"] = [parse_float(el.string) for el in
                                                   soup.find_all('a', string=price_pattern)]

                        try:
                            product["other_prices"].remove(product["current_price"])
                        except ValueError:
                            with open("test.txt", 'w') as fh:
                                fh.write(response.text)
                        if product["new_price"]:
                            product["other_prices"].remove(product["new_price"])

                        candidates.append(product)
                        print(product)
                        time.sleep(random.randrange(PRODUCT_RANGE[0], PRODUCT_RANGE[1]))

        for candidate in calculate_price_difference(candidates):
            price_notification(**candidate)

        visited = products[:BATCH_SIZE]

        duration = random.randrange(CYCLE_RANGE[0], CYCLE_RANGE[1])
        logger.info(f"Cycle done; sleep for {duration} seconds")
        time.sleep(duration)


if __name__ == "__main__":
    main()
