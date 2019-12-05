"""Contains function for retrieving proxies and filtering slow ones"""
import logging

import requests

logger = logging.getLogger(__name__)


def retrieve_proxies(urls: list) -> list:
    def download() -> list:
        for url in urls:
            try:
                proxies = requests.get(url).text.split()
            except requests.RequestException:
                logger.error(f"Proxies could not be retrieved for {url}", exc_info=1)
            else:
                yield proxies

    return [item for proxy in download() for item in proxy]


def filter_proxies(proxies: list, test_url: str, connect_timeout: float = 1.0, read_timeout: float = 0.3,
                   https: bool = True) -> list:
    protocol = "https" if https else "http"

    checked = []

    for proxy in proxies:
        try:
            requests.get(test_url, proxies={protocol: proxy}, timeout=(connect_timeout, read_timeout))
        except requests.RequestException:
            continue
        checked.append(proxy)
    return checked
