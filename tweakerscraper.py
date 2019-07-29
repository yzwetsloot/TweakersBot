import time
import re
import random
import sys

from bs4 import BeautifulSoup, SoupStrainer
import requests
import lxml

from pricedifference import calculate_price_difference
from notificationemail import send_error_notification, send_price_notification

START_PAGE = "https://tweakers.net/aanbod/zoeken/"

A_TAGS = SoupStrainer('a')


def parse_float(price: str) -> float:
    return float(re.sub("€|\s|-|\.", '', price).replace(",", "."))


def main():
    old_links_list = []

    with open("config/cookieconfig.txt") as fh:
        cookies = [line.strip() for line in fh]

    index = 0

    headers = {
        "Accept": "text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-NL",
        "Cache-Control": "max-age=0",
        "Cookie": cookies[0],
        "Host": "tweakers.net",
        "Referer": "https://tweakers.net/",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763 "
    }

    while True:
        print("Start scraping...")
        start_time = time.time()
        scrape_count = 0
        products = []
        error_count = 0

        response = requests.get(START_PAGE, headers=headers)
        soup = BeautifulSoup(response.content, "lxml", parse_only=A_TAGS)

        product_links = [link.get("href") for link in soup.find_all(class_=["thumb small", "thumb small empty"])]

        for product_link in product_links[0:4]:
            product_info = {"link": product_link}

            if product_link not in old_links_list:
                response = requests.get(product_link, headers=headers)
                soup = BeautifulSoup(response.content, "lxml", parse_only=A_TAGS)
                product_page = soup.find(class_=["thumb normal", "thumb normal empty"])

                if product_page:
                    product_page_link = product_page.get("href")

                    while True:
                        response = requests.get(product_page_link, headers=headers)
                        soup = BeautifulSoup(response.content, "lxml", parse_only=A_TAGS)

                        pricewatch_price = soup.find(string=re.compile("^€ ([0-9])+,(-|[0-9]+)$"))

                        product_info["price_new"] = parse_float(pricewatch_price.string) if pricewatch_price else None

                        try:
                            other_sellers_page = soup.find(
                                href=re.compile("https://tweakers.net/pricewatch/.*(aanbod).*")).get(
                                "href")
                        except Exception as err:
                            if error_count > 6:
                                send_error_notification("Stopped program")
                                sys.exit()

                            send_error_notification(str(err))

                            index += 1
                            headers["Cookie"] = cookies[index % 3]

                            error_count += 1

                            continue

                        break

                    response = requests.get(other_sellers_page, headers=headers)
                    soup = BeautifulSoup(response.content, "lxml", parse_only=A_TAGS)
                    other_prices = soup.find_all(string=re.compile("€ ([0-9\.])+,(-|[0-9]+)"))

                    product_info["price_old"] = [parse_float(price.string)
                                                 for price in other_prices
                                                 if parse_float(price.string) != product_info["price_new"]]

                    products.append(product_info)

                    scrape_count += 1

        duration = time.time() - start_time
        print(f"Scraped {scrape_count} in {duration} seconds")

        if scrape_count > 0:
            for i, j in enumerate(calculate_price_difference(products)):
                if j:
                    send_price_notification(products[i])

        old_links_list = product_links[0:4]

        timeout = random.randrange(85, 145)
        print(f"Start sleeping for {timeout} seconds...")
        time.sleep(timeout)


if __name__ == "__main__":
    main()
