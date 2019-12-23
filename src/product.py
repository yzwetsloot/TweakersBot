"""Contains functions for retrieving products from the Tweakers.net marketplace"""
from itertools import count
import json
import random
import re
import time
import typing

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

with open("../config/config.json") as config:
    parameters = json.load(config)
    locators = parameters["locators"]

with open("../resources/keywords.txt") as keywords:
    keywords = keywords.read().splitlines()

START_PAGE = parameters["start_page"]
BATCH_SIZE = parameters["batch_size"]
CYCLE_RANGE = parameters["cycle_range"]
PAGE_RANGE = parameters["page_range"]
TIMEOUT = parameters["timeout"]
DEBUG = parameters["debug"]

BUTTON_CLASS_NAME = locators["button_class_name"]
PRODUCT_PATH = locators["product_path"]
CURRENT_PRICE_PATH = locators["current_price_path"]
PRICEWATCH_PATH = locators["pricewatch_path"]
PRICEWATCH_PRICE_CLASS_NAME = locators["pricewatch_price_class_name"]
OTHER_SELLERS_ID = locators["other_sellers_id"]
OTHER_SELLERS_PRICE_PATH = locators["other_sellers_price_path"]


price_pattern = re.compile("€ [0-9.]+,(-|[0-9]+)")

visited = []


def parse_float(price: str) -> float:
    return float(re.sub("€|\\s|-|\\.", '', price).replace(",", "."))


def element_exists(locator: str, finder: typing.Callable) -> bool:
    try:
        finder(locator)
    except NoSuchElementException:
        return False
    return True


def get_products(proxy: str) -> list:
    global visited

    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("window-size=1920,1080")
    options.add_argument('--proxy-server=%s' % proxy)

    try:
        with webdriver.Chrome(options=options) as driver:
            driver.set_page_load_timeout(TIMEOUT)

            driver.get(START_PAGE)

            try:
                button = driver.find_element_by_class_name(BUTTON_CLASS_NAME)
            except NoSuchElementException:
                if DEBUG:
                    with open("../debug/page.html", 'w') as debug:
                        debug.write(str(driver.page_source.encode("utf-8")))
                time.sleep(random.randrange(CYCLE_RANGE[0], CYCLE_RANGE[1]))
                return []

            time.sleep(random.randrange(PAGE_RANGE[0], PAGE_RANGE[1]))
            button.click()

            links, products = [], []

            for index in range(BATCH_SIZE):
                product_link = driver.find_element_by_xpath(PRODUCT_PATH.format(index + 1))
                links.append(product_link.get_attribute("href"))

            for link in links:
                if link in visited:
                    continue
                try:
                    product_link = driver.find_element(By.CSS_SELECTOR, "a[href='{}']".format(link))
                except NoSuchElementException:
                    continue

                time.sleep(random.randrange(PAGE_RANGE[0], PAGE_RANGE[1]))
                product_link.click()

                if any(keyword in driver.page_source for keyword in keywords):
                    time.sleep(random.randrange(PAGE_RANGE[0], PAGE_RANGE[1]))
                    driver.back()
                    continue

                product = {"url": driver.current_url, "current_price": None, "new_price": 0.0, "other_prices": []}

                if element_exists(CURRENT_PRICE_PATH, driver.find_element_by_xpath):
                    current_price = driver.find_element_by_xpath(CURRENT_PRICE_PATH).text
                    match = re.match(price_pattern, current_price)
                    if match:
                        product["current_price"] = parse_float(match.group(0))
                    else:
                        time.sleep(random.randrange(PAGE_RANGE[0], PAGE_RANGE[1]))
                        driver.back()
                        continue
                else:
                    time.sleep(random.randrange(PAGE_RANGE[0], PAGE_RANGE[1]))
                    driver.back()
                    continue

                if element_exists(PRICEWATCH_PATH, driver.find_element_by_xpath):
                    pricewatch_link = driver.find_element_by_xpath(PRICEWATCH_PATH)
                    time.sleep(random.randrange(PAGE_RANGE[0], PAGE_RANGE[1]))
                    pricewatch_link.click()

                    if element_exists(PRICEWATCH_PRICE_CLASS_NAME, driver.find_element_by_class_name):
                        new_price = driver.find_element_by_class_name(PRICEWATCH_PRICE_CLASS_NAME).text
                        match = re.match(price_pattern, new_price)
                        if match:
                            product["new_price"] = parse_float(match.group(0))

                    if element_exists(OTHER_SELLERS_ID, driver.find_element_by_id):
                        temp = driver.find_element_by_id(OTHER_SELLERS_ID)
                        try:
                            button = temp.find_element_by_tag_name('a')
                        except NoSuchElementException:
                            time.sleep(random.randrange(PAGE_RANGE[0], PAGE_RANGE[1]))
                            driver.back()
                            time.sleep(random.randrange(PAGE_RANGE[0], PAGE_RANGE[1]))
                            driver.back()
                            continue

                        button.click()
                        time.sleep(random.randrange(PAGE_RANGE[0], PAGE_RANGE[1]))

                        for counter in count(start=1):
                            seller_price_link = OTHER_SELLERS_PRICE_PATH.format(counter)
                            if element_exists(seller_price_link, driver.find_element_by_xpath):
                                seller_price = driver.find_element_by_xpath(seller_price_link).text
                                match = re.match(price_pattern, seller_price)
                                if match:
                                    product["other_prices"].append(parse_float(match.group(0)))
                            else:
                                break

                        if product["current_price"] in product["other_prices"]:
                            product["other_prices"].remove(product["current_price"])

                        time.sleep(random.randrange(PAGE_RANGE[0], PAGE_RANGE[1]))
                        driver.back()
                    time.sleep(random.randrange(PAGE_RANGE[0], PAGE_RANGE[1]))
                    driver.back()
                time.sleep(random.randrange(PAGE_RANGE[0], PAGE_RANGE[1]))
                driver.back()

                if DEBUG:
                    print(product)

                products.append(product)
    except TimeoutException:
        raise TimeoutError

    visited = links
    return products
