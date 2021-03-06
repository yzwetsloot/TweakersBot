import json
import logging.config
import random
import time

import yaml

from notification import price_notification
from price import candidate
from product import get_products

with open("../config/log.yaml") as config:
    parameters = yaml.safe_load(config.read())
    logging.config.dictConfig(parameters)

logger = logging.getLogger(__name__)

with open("../config/config.json") as config:
    parameters = json.load(config)

with open("../resources/proxies.txt") as proxies:
    proxies = proxies.read().splitlines()

CYCLE_RANGE = parameters["cycle_range"]


def main() -> None:
    while True:
        try:
            products = get_products(proxies[random.randrange(0, len(proxies) - 1)])
        except TimeoutError:
            logger.error("Page could not be loaded")
            continue

        logger.info(f"Retrieved {len(products)} products")

        for product in products:
            if candidate(product):
                price_notification(**product)

        duration = random.randrange(CYCLE_RANGE[0], CYCLE_RANGE[1])
        logger.info(f"Cycle done; sleep for {duration} seconds")
        time.sleep(duration)


if __name__ == "__main__":
    main()
