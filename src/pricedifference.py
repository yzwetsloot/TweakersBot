PROFIT_MARGIN = 70

NEW_OLD_MARGIN = 10

OUTLIER_REGION = 0.1

UPPER_BOUND = 700


def calculate_price_difference(products: list) -> iter:
    for product in products:
        new_price = product["price_new"]
        ad_price = product["price"]
        other_sellers = product["price_old"]

        if other_sellers:
            filtered = filter(lambda x: x / ad_price > OUTLIER_REGION, other_sellers)
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
            abs_diff = rel_diff = 0
            new_price = 0

        if lowest_price == ad_price:
            other_abs_diff = other_rel_diff = 0
        else:
            other_abs_diff = round(lowest_price - ad_price)
            other_rel_diff = compute_percentage(ad_price / lowest_price)

        product["price_difference"] = [abs_diff, rel_diff, other_abs_diff, other_rel_diff]

        if ad_price <= UPPER_BOUND and ((lowest_price - PROFIT_MARGIN + NEW_OLD_MARGIN > ad_price) or
                                (determine_margin(new_price, ad_price) and not other_sellers)):
            yield True
        else:
            yield False


def compute_percentage(number: int) -> int:
    return round((1 - number) * 100)


def determine_margin(determinant: int, value: int) -> int:
    return determinant * 0.75 - PROFIT_MARGIN > value
