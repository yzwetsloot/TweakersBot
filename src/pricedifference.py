def calculate_price_difference(products: list) -> iter:
    for product_info in products:
        price_new = product_info["price_new"]
        price_ad = product_info["price"]
        other_sellers = product_info["price_old"]

        if other_sellers:
            price_lowest = sorted(other_sellers)[0]
        else:
            price_lowest = price_ad

        if price_new:
            abs_diff = round(price_new - price_ad)
            rel_diff = compute_percentage(price_ad / price_new)
        else:
            abs_diff = rel_diff = 0

        if price_lowest == price_ad:
            other_abs_diff = other_rel_diff = 0
        else:
            other_abs_diff = round(price_lowest - price_ad)
            other_rel_diff = compute_percentage(price_ad / price_lowest)

        product_info["price difference"] = [abs_diff, rel_diff, other_abs_diff, other_rel_diff]

        if ((abs_diff > 90 and (len(other_sellers) == 1 or other_abs_diff > 10)) or other_abs_diff > 10) \
                and price_ad < 900:
            yield True
        else:
            yield False


def compute_percentage(number: int) -> int:
    return round((1 - number) * 100)
