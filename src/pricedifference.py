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


def calculate_price_difference(products: list) -> iter:
    for product in products:
        current_price = product["current_price"]
        new_price = product["new_price"]
        other_sellers = product["other_prices"]

        if not current_price:
            continue

        if other_sellers:
            filtered = list(filter(lambda el: el / current_price > OUTLIER_TRESHOLD, other_sellers))
            if filtered:
                lowest_price = sorted(filtered)[0]
            else:
                lowest_price = current_price
        else:
            lowest_price = current_price

        if new_price:
            abs_diff = round(new_price - current_price)
            rel_diff = compute_percentage(current_price / new_price)
        else:
            abs_diff = rel_diff = new_price = 0

        if lowest_price == current_price:
            other_abs_diff = other_rel_diff = 0
        else:
            other_abs_diff = round(lowest_price - current_price)
            other_rel_diff = compute_percentage(current_price / lowest_price)

        product["absolute_new"] = abs_diff
        product["relative_new"] = rel_diff
        product["absolute_others"] = other_abs_diff
        product["relative_others"] = other_rel_diff

        if current_price <= MAX_PRICE and ((lowest_price - PROFIT_MARGIN > current_price) or
                                           (determine_margin(new_price, current_price) and
                                            (not other_sellers) and SINGLE_PRODUCT)):
            yield product
