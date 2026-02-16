# core/agent.py
import re
from core.agent_tools import filter_products, get_cheapest_product
from core.normalizer import infer_category

def is_greeting(text: str) -> bool:
    greetings = {
        "hi", "hello", "hey",
        "good morning", "good afternoon", "good evening"
    }
    return text.lower().strip() in greetings


def handle_user_query(query: str, products: list):
    query_lower = query.lower().strip()

    # 1️⃣ Greeting
    if is_greeting(query_lower):
        return {
            "message": "Hello! 👋 What can I help you with today?",
            "results": []
        }

    # 2️⃣ Detect max price
    max_price = None
    match = re.search(r"under\s+(\d+)", query_lower)
    if match:
        max_price = int(match.group(1))

    # 3️⃣ Detect category
    category = infer_category(query_lower)

    # 4️⃣ Filter products
    results = filter_products(
        products,
        max_price=max_price,
        category=category
    )

    # 5️⃣ Fallback: cheapest
    if not results and max_price:
        cheapest = get_cheapest_product(products, category=category)
        if cheapest:
            return {
                "message": (
                    f"I don’t have options under ${max_price}. "
                    f"The most affordable option is {cheapest['product_name']} "
                    f"at ${int(cheapest['price_usd'])}."
                ),
                "results": [cheapest]
            }

        return {
            "message": "I couldn’t find any matching products right now.",
            "results": []
        }

    # 6️⃣ Normal response
    return {
        "message": "Here are some options:",
        "results": results
    }
