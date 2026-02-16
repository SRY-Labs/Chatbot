def filter_products(
    products,
    max_price=None,
    category=None,
    available_only=True,
    exclude_name=None
):
    results = []

    for p in products:
        if available_only and not p["available"]:
            continue
        if max_price and p["price_usd"] > max_price:
            continue
        if category and p["category"] != category:
            continue
        if exclude_name and exclude_name.lower() in p["product_name"].lower():
            continue

        results.append(p)

    return results

def get_cheapest_product(products, category=None):
    filtered = [
        p for p in products
        if (not category or p["category"] == category)
        and p["available"]
    ]

    if not filtered:
        return None

    return min(filtered, key=lambda p: p["price_usd"])
