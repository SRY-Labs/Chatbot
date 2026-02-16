import os
import json
import requests

from core.data_loader import load_products
from core.agent_tools import filter_products
from core.formatter import format_response


def scrape_products_json():
    base_url = "https://robertallendesign.com"
    url = f"{base_url}/collections/quick-ship/products.json"

    r = requests.get(url, timeout=10)
    r.raise_for_status()

    products = r.json()["products"]
    results = []

    for p in products:
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
            "available": True
        })

    return results


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    os.makedirs(DATA_DIR, exist_ok=True)

    output_path = os.path.join(DATA_DIR, "products.json")

    data = scrape_products_json()
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✅ Saved {output_path}")

products = load_products()

# Example user query
user_query = "Show me sofas under 3000"

results = filter_products(
    products,
    max_price=3000,
    category="sofa"
)

response = format_response(results)
print(response)
