"""Contains functions for retrieving products"""
from itertools import count
import json
import re

from seleniumwire import webdriver
from selenium.common.exceptions import NoSuchElementException

with open("../config/config.json") as config:
    parameters = json.load(config)
    xpaths = parameters["xpaths"]

START_PAGE = parameters["start_page"]
BATCH_SIZE = parameters["batch_size"]
CYCLE_RANGE = parameters["cycle_range"]
USER_AGENT = parameters["user_agent"]

BUTTON_PATH = xpaths["button_path"]
PRODUCT_PATH = xpaths["product_path"]
CURRENT_PRICE_PATH = xpaths["current_price_path"]
PRICEWATCH_PATH = xpaths["pricewatch_path"]
PRICEWATCH_PRICE_PATH = xpaths["pricewatch_price_path"]
OTHER_SELLERS_PATH = xpaths["other_sellers_path"]
OTHER_SELLERS_PRICE_PATH = xpaths["other_sellers_price_path"]


price_pattern = re.compile("\\s*€ [0-9.]+,(-|[0-9]+)\\s*")

visited = []


def parse_float(price: str) -> float:
    return float(re.sub("€|\\s|-|\\.", '', price).replace(",", "."))


def check_element_exists(xpath: str, driver: webdriver) -> bool:
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def get_products() -> list:
    global visited

    options = webdriver.ChromeOptions()
    options.headless = True

    with webdriver.Chrome(options=options) as driver:
        driver.maximize_window()

        driver.get(START_PAGE)
        button = driver.find_element_by_xpath(BUTTON_PATH)
        button.click()

        product_links = []
        products = []

        for index in range(BATCH_SIZE):
            product_link = driver.find_element_by_xpath(PRODUCT_PATH.format(index + 1))
            product_links.append(product_link)

        for product_link in product_links:
            product_link.click()
            product = {"url": driver.current_url, "current_price": None, "new_price": None, "other_prices": []}

            if check_element_exists(CURRENT_PRICE_PATH, driver):
                current_price = driver.find_element_by_xpath(CURRENT_PRICE_PATH).text
                if re.match(price_pattern, current_price):
                    product["current_price"] = parse_float(current_price)

            if check_element_exists(PRICEWATCH_PATH, driver):
                pricewatch_link = driver.find_element_by_xpath(PRICEWATCH_PATH)
                pricewatch_link.click()

                if check_element_exists(PRICEWATCH_PRICE_PATH, driver):
                    new_price = driver.find_element_by_xpath(PRICEWATCH_PRICE_PATH).text
                    if re.match(price_pattern, new_price):
                        product["new_price"] = parse_float(new_price)

                other_sellers_link = driver.find_element_by_xpath(OTHER_SELLERS_PATH)
                other_sellers_link.click()

                for counter in count(start=1):
                    seller_price_link = OTHER_SELLERS_PRICE_PATH.format(counter)
                    if check_element_exists(seller_price_link, driver):
                        seller_price = driver.find_element_by_xpath(seller_price_link).text
                        if re.match(price_pattern, seller_price):
                            product["other_prices"].append(parse_float(seller_price))
                    else:
                        break

                driver.back()
                driver.back()

            driver.back()

            products.append(product)

    visited = product_links
    return products
