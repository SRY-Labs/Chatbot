import json
from core.normalizer import infer_category

def load_products(path="data/products.json"):
    with open(path) as f:
        products = json.load(f)

    for p in products:
        p["category"] = infer_category(p["product_name"])

    return products
