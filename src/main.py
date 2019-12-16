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
from identity import get_identity

with open("../config/log.yaml") as config:
    parameters = yaml.safe_load(config.read())
    logging.config.dictConfig(parameters)

logger = logging.getLogger(__name__)

link_tags = SoupStrainer('a')

price_pattern = re.compile("\\s*€ [0-9.]+,(-|[0-9]+)\\s*")
pricewatch_pattern = re.compile("^€ [0-9.]+,(-|[0-9]+)$")
sellers_pattern = re.compile(".*pricewatch/.*/aanbod/\\s*")
recaptcha_pattern = re.compile(".*Captcha.*")

with open("../config/config.json") as config:
    parameters = json.load(config)

START_PAGE = parameters["start_page"]
BATCH_SIZE = parameters["batch_size"]
TIMEOUT = parameters["timeout"]
CYCLE_RANGE = parameters["cycle_range"]
PRODUCT_RANGE = parameters["product_range"]

proxy, headers, cookies = None, None, None


def parse_float(price: str) -> float:
    return float(re.sub("€|\\s|-|\\.", '', price).replace(",", "."))


def change_identity() -> tuple:
    global proxy, headers, cookies
    while True:
        proxies = open("../resources/proxies.txt").read().splitlines()
        proxy = proxies[random.randrange(0, len(proxies) - 1)]

        try:
            headers, cookies = get_identity(proxy)
        except Exception as err:
            print(err)
            continue
        return proxy, headers, cookies


def fetch_page(url: str, parse_only: SoupStrainer = None) -> BeautifulSoup:
    global proxy, headers, cookies
    while True:
        try:
            response = requests.get(url, headers=headers, cookies=cookies, proxies={"https": proxy})
            break
        except requests.RequestException:
            proxy, headers, cookies = change_identity()
            logger.error(f"Connection error occurred; switch to {proxy}")
            time.sleep(TIMEOUT)
    return BeautifulSoup(response.content, "lxml", parse_only=parse_only)


def main() -> None:
    global proxy, headers, cookies
    proxy, headers, cookies = change_identity()

    visited = []

    while True:
        candidates = []
        soup = fetch_page(START_PAGE, link_tags)

        products = [{"url": product["href"].strip(), "current_price": parse_float(product.string)}
                    for product in soup.find_all('a', string=price_pattern)]

        for product in products[:BATCH_SIZE]:
            if product["url"] not in visited:
                soup = fetch_page(product["url"], link_tags)
                pricewatch_page = soup.find(class_=["thumb normal", "thumb normal empty"])

                if pricewatch_page:
                    soup = fetch_page(pricewatch_page["href"])
                    while True:
                        if soup.find(string=recaptcha_pattern):
                            logger.info(f"ReCaptcha presented; retrieve cookies")
                            proxy, headers, cookies = change_identity()
                            time.sleep(TIMEOUT)
                            continue
                        break

                    pricewatch_price = soup.find(string=pricewatch_pattern)
                    product["new_price"] = parse_float(pricewatch_price.string) if pricewatch_price else None

                    sellers_page = soup.find(href=sellers_pattern)

                    if sellers_page:
                        soup = fetch_page(sellers_page["href"])
                        while True:
                            if soup.find(string=recaptcha_pattern):
                                logger.info(f"ReCaptcha presented; retrieve cookies")
                                proxy, headers, cookies = change_identity()
                                continue
                            break

                        product["other_prices"] = [parse_float(el.string) for el in
                                                   soup.find_all('a', string=price_pattern)]

                        product["other_prices"].remove(product["current_price"])

                        if product["new_price"]:
                            product["other_prices"].remove(product["new_price"])

                        candidates.append(product)
                        time.sleep(random.randrange(PRODUCT_RANGE[0], PRODUCT_RANGE[1]))

        for candidate in calculate_price_difference(candidates):
            price_notification(**candidate)

        visited = products[:BATCH_SIZE]

        duration = random.randrange(CYCLE_RANGE[0], CYCLE_RANGE[1])
        logger.info(f"Cycle done; sleep for {duration} seconds")
        time.sleep(duration)


if __name__ == "__main__":
    main()
