from datetime import datetime
import time
import re
import random
import sys

from bs4 import BeautifulSoup, SoupStrainer
import requests

from pricedifference import calculate_price_difference
from emailnotification import send_error_notification, send_price_notification
from requestcookies import get_cookies

START_PAGE = "https://tweakers.net/aanbod/zoeken/"

A_TAGS = SoupStrainer('a')


def main() -> None:
    total_start_time = datetime.now()
    old_links_list = []
    cookies = get_cookies()

    headers = {
        "Accept": "text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-NL",
        "Cache-Control": "max-age=0",
        "Host": "tweakers.net",
        "Referer": "https://tweakers.net/",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763 "
    }

    while True:
        print(f"[LOG] {datetime.now() - total_start_time} | Start scraping...")
        start_time = time.time()
        scrape_count = 0
        products = []
        error_count = 0

        response = requests.get(START_PAGE, headers=headers, cookies=cookies)
        soup = BeautifulSoup(response.content, "lxml", parse_only=A_TAGS)

        product_links = [(link.get("href"), parse_float(link.string))
                         for link in soup.find_all('a', string=re.compile("€ ([0-9\.])+,(-|[0-9]+)"))]

        for product_link in product_links[0:4]:
            product_info = {"link": product_link[0], "price": product_link[1]}

            if product_link not in old_links_list:
                response = requests.get(product_link[0], headers=headers, cookies=cookies)
                soup = BeautifulSoup(response.content, "lxml", parse_only=A_TAGS)
                product_page = soup.find(class_=["thumb normal", "thumb normal empty"])

                if product_page:
                    product_page_link = product_page.get("href")

                    while True:
                        response = requests.get(product_page_link, headers=headers, cookies=cookies)
                        soup = BeautifulSoup(response.content, "lxml", parse_only=A_TAGS)

                        pricewatch_price = soup.find(string=re.compile("^€ ([0-9.])+,(-|[0-9]+)$"))

                        product_info["price_new"] = parse_float(pricewatch_price.string) if pricewatch_price else None

                        try:
                            other_sellers_page = soup.find(
                                href=re.compile("https://tweakers.net/pricewatch/.*(aanbod).*")).get(
                                "href")
                        except AttributeError:

                            if error_count > 3:
                                send_error_notification("Stopped program")
                                print(f"[LOG] Total runtime is {datetime.now() - total_start_time}")
                                sys.exit()

                            error_count += 1

                            cookies = get_cookies()

                            time.sleep(random.randrange(30, 60))
                            print(f"[LOG] {datetime.now() - total_start_time} | Switch to next available cookie")

                            continue

                        break

                    time.sleep(random.randrange(1, 4))

                    response = requests.get(other_sellers_page, headers=headers, cookies=cookies)
                    soup = BeautifulSoup(response.content, "lxml", parse_only=A_TAGS)
                    other_prices = soup.find_all(string=re.compile("€ ([0-9.])+,(-|[0-9]+)"), title=False)

                    product_info["price_old"] = [parse_float(price.string)
                                                 for price in other_prices
                                                 if parse_float(price.string) != product_info["price_new"]]

                    products.append(product_info)

                    scrape_count += 1

        duration = time.time() - start_time
        print(f"[LOG] {datetime.now() - total_start_time} | Scraped {scrape_count} in {duration} seconds")

        if scrape_count > 0:
            for i, j in enumerate(calculate_price_difference(products)):
                if j:
                    send_price_notification(products[i])

        old_links_list = product_links[0:4]

        timeout = random.randrange(85, 250)
        print(f"[LOG] {datetime.now() - total_start_time} | Start sleeping for {timeout} seconds...\n")
        time.sleep(timeout)


def parse_float(price: str) -> float:
    return float(re.sub("€|\s|-|\.", '', price).replace(",", "."))


if __name__ == "__main__":
    main()
