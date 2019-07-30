def calculate_price_difference(products: list):
    for product_info in products:
        price_new = product_info["price_new"]
        price_old = sorted(product_info["price_old"])

        if not product_info["price_old"]:
            continue

        if len(price_old) > 1:
            # Price difference relative to all other sellers
            other_abs_diff = round(price_old[1] - price_old[0])
            other_rel_diff = compute_percentage(price_old[0] / price_old[1])
        else:
            other_abs_diff = other_rel_diff = 0

        if price_new:
            # Price difference relative to new price
            abs_diff = round(price_new - price_old[0])
            rel_diff = compute_percentage(price_old[0] / price_new)
        else:
            abs_diff = rel_diff = 0

        abs_mean_diff = round(compute_mean(product_info["price_old"]) - price_old[0])
        rel_mean_diff = compute_percentage(price_old[0] / compute_mean(product_info["price_old"]))

        product_info["price difference"] = \
            [abs_diff, rel_diff, other_abs_diff, other_rel_diff, abs_mean_diff, rel_mean_diff]

        if (rel_diff > 35 and abs_diff > 90) or \
                ((other_rel_diff > 30 and other_abs_diff > 50) and (abs_diff > 100)) or \
                (abs_mean_diff > 100 or rel_mean_diff > 40) and \
                (price_old[0] < 800 or abs_diff < 800):
            yield True
        else:
            yield False


def compute_mean(price_list: list) -> int:
    return sum(price_list) / len(price_list)


def compute_percentage(number: int) -> int:
    return round((1 - number) * 100)
