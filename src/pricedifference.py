import json

with open("../config/config.json") as config:
    parameters = json.load(config)

PROFIT_MARGIN = parameters["profit_margin"]
MAX_PRICE = parameters["max_price"]
OUTLIER_REGION = parameters["outlier_region"]
SINGLE_PRODUCT = parameters["single_product"]


def calculate_price_difference(products: list) -> iter:
    for product in products:
        new_price = product["new"]
        ad_price = product["current"]
        other_sellers = product["sellers"]

        if other_sellers:
            filtered = list(filter(lambda x: x / ad_price > OUTLIER_REGION, other_sellers))
            if filtered:
                lowest_price = sorted(filtered)[0]
            else:
                lowest_price = ad_price
        else:
            lowest_price = ad_price

        if new_price:
            abs_diff = round(new_price - ad_price)
            rel_diff = compute_percentage(ad_price / new_price)
        else:
            abs_diff = rel_diff = new_price = 0

        if lowest_price == ad_price:
            other_abs_diff = other_rel_diff = 0
        else:
            other_abs_diff = round(lowest_price - ad_price)
            other_rel_diff = compute_percentage(ad_price / lowest_price)

        product["price_difference"] = [abs_diff, rel_diff, other_abs_diff, other_rel_diff]

        if ad_price <= MAX_PRICE and ((lowest_price - PROFIT_MARGIN > ad_price) or
                                      (determine_margin(new_price, ad_price) and
                                       (not other_sellers) and SINGLE_PRODUCT)):
            yield product


def compute_percentage(number: int) -> int:
    return round((1 - number) * 100.0)


def determine_margin(determinant: int, value: int) -> int:
    return determinant * 0.75 - PROFIT_MARGIN > value
