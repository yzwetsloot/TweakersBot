def calculate_price_difference(products: list):
    for product_info in products:
        price_new = product_info["price_new"]
        price_old = sorted(product_info["price_old"])

        if len(price_old) == 0:
            yield False

        if len(price_old) > 1:
            # Price difference relative to all other sellers
            other_abs_diff = round(price_old[1] - price_old[0])
            other_rel_diff = round((1 - (price_old[0] / price_old[1])) * 100)
        else:
            other_abs_diff = other_rel_diff = 0

        if price_new:
            # Price difference relative to new price
            abs_diff = round(price_new - price_old[0])
            rel_diff = round((1 - (price_old[0] / price_new)) * 100)
        else:
            abs_diff = rel_diff = 0

        product_info["price difference"] = [abs_diff, rel_diff, other_abs_diff, other_rel_diff]

        if (rel_diff > 35 and abs_diff > 50) or (other_rel_diff > 30 and other_abs_diff > 50):
            yield True
        else:
            yield False
