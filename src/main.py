import json
import logging.config
import re

from bs4 import BeautifulSoup, SoupStrainer
import requests
import yaml

from notification import price_notification
from pricedifference import calculate_price_difference
from requestcookies import get_cookies

with open("../config/log.yaml") as config:
    parameters = yaml.safe_load(config.read())
    logging.config.dictConfig(parameters)

logger = logging.getLogger(__name__)

link_tags = SoupStrainer('a')

price_pattern = re.compile("\\s*€ [0-9.]+,(-|[0-9]+)\\s*")
pricewatch_pattern = re.compile("^€ [0-9.]+,(-|[0-9]+)$")
sellers_pattern = re.compile(".*/aanbod/\\s")
recaptcha_pattern = re.compile("recaptcha")

with open("../config/config.json") as config:
    parameters = json.load(config)

START_PAGE = parameters["start_page"]
BATCH_SIZE = parameters["batch_size"]
HEADERS = parameters["headers"]


def parse_float(price: str) -> float:
    return float(re.sub("€|\\s|-|\\.", '', price).replace(",", "."))


def main() -> None:
    visited = []
    cookies = get_cookies()

    while True:
        candidates = []

        try:
            response = requests.get(START_PAGE, headers=HEADERS, cookies=cookies)
        except requests.RequestException:
            pass
        soup = BeautifulSoup(response.content, "lxml", parse_only=link_tags)

        products = [{"url": product["href"].strip(), "current_price": parse_float(product.string)}
                    for product in soup.find_all('a', string=price_pattern)]

        for product in products[:BATCH_SIZE]:
            if product["url"] not in visited:
                try:
                    response = requests.get(product["url"], headers=HEADERS, cookies=cookies)
                except requests.RequestException:
                    pass
                soup = BeautifulSoup(response.content, "lxml", parse_only=link_tags)
                pricewatch_page = soup.find(class_=["thumb normal", "thumb normal empty"])

                if pricewatch_page:
                    try:
                        response = requests.get(pricewatch_page["href"], headers=HEADERS, cookies=cookies)
                    except requests.RequestException:
                        pass
                    soup = BeautifulSoup(response.content, "lxml", parse_only=link_tags)

                    pricewatch_price = soup.find(string=pricewatch_pattern)
                    product["new_price"] = parse_float(pricewatch_price.string) if pricewatch_price else None

                    while True:
                        recaptcha = soup.find(recaptcha_pattern)
                        if recaptcha:
                            # TODO resolve cookie-issue
                            cookies = get_cookies()
                            continue
                        break

                    sellers_page = soup.find(href=sellers_pattern)
                    try:
                        response = requests.get(sellers_page["href"], headers=HEADERS, cookies=cookies)
                    except requests.RequestException:
                        pass
                    soup = BeautifulSoup(response.content, "lxml", parse_only=link_tags)
                    product["other_prices"] = [parse_float(el.string) for el in
                                               soup.find_all(string=price_pattern, parse_only=link_tags)]
                    product["other_prices"].remove(product["current_price"])

                    candidates.append(product)

        for candidate in calculate_price_difference(candidates):
            price_notification(candidate)

        visited = products[:BATCH_SIZE]


if __name__ == "__main__":
    main()
