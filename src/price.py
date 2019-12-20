"""Contains method for determining whether product is a candidate"""
import json

with open("../config/config.json") as config:
    parameters = json.load(config)

PROFIT_TRESHOLD = parameters["profit_treshold"]
PROFIT_MARGIN = parameters["profit_margin"]
MAX_PRICE = parameters["max_price"]
OUTLIER_TRESHOLD = parameters["outlier_treshold"]
SINGLE_PRODUCT = parameters["single_product"]


def compute_percentage(number: int) -> int:
    return round((1 - number) * 100.0)


def determine_margin(determinant: int, value: int) -> int:
    return determinant * PROFIT_TRESHOLD - PROFIT_MARGIN > value


def candidate(product: dict) -> bool:
    current_price, new_price, other_prices = product["current_price"], product["new_price"], product["other_prices"]

    filtered = list(filter(lambda el: el / current_price > OUTLIER_TRESHOLD, other_prices))
    lowest_price = sorted(filtered)[0] if filtered else current_price

    product.update({"absolute_new": round(new_price - current_price),
                    "relative_new": compute_percentage(current_price / new_price) if new_price > 0 else None,
                    "absolute_others": round(lowest_price - current_price),
                    "relative_others": compute_percentage(current_price / lowest_price)})

    if current_price <= MAX_PRICE and ((lowest_price - PROFIT_MARGIN > current_price) or
                                       (determine_margin(new_price, current_price) and
                                        (not other_prices) and SINGLE_PRODUCT)):
        return True
