import os
import json
import requests


def scrape_products_json():
    base_url = "https://robertallendesign.com"
    url = f"{base_url}/collections/quick-ship/products.json"

    r = requests.get(url, timeout=10)
    r.raise_for_status()

    products = r.json()["products"]
    results = []

    for p in products:
        # 🔍 Extract Finish (color) at PRODUCT level
        colors = []
        for option in p.get("options", []):
            option_name = option["name"].lower()
            if option_name in ["finish", "color", "colour"]:
                colors = option.get("values", [])
                break

        # 💰 Pricing from variants
        available_variants = [v for v in p["variants"] if v["available"]]
        if not available_variants:
            continue

        lowest_variant = min(
            available_variants,
            key=lambda v: float(v["price"])
        )

        results.append({
            "product_name": p["title"],
            "product_url": f"{base_url}/products/{p['handle']}",
            "price_usd": float(lowest_variant["price"]),
            "compare_at_price": float(lowest_variant["compare_at_price"])
            if lowest_variant.get("compare_at_price") else None,
            "available": True,
            "colors": colors
        })

    return results


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(BASE_DIR, "products.json")

    data = scrape_products_json()

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Saved products with Finish colors to {output_path}")
