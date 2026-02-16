# core/agent.py
import re
from core.agent_tools import filter_products, get_cheapest_product
from core.normalizer import infer_category

SUPPORTED_CATEGORIES = {
    "sofa",
    "loveseat",
    "armchair",
    "ottoman",
    "sofa bed"
}

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

    # 🔧 Normalize category safely
    if category:
        category = category.strip().lower()

    # 🚨 Unsupported or unknown category
    if category and category not in SUPPORTED_CATEGORIES:
        suggestions = filter_products(products)[:3]

        # Treat any "other*" as unknown
        if category.startswith("other"):
            message = (
                "Sorry, we don’t have that product right now. "
                "But I’d be happy to show you some other options you might like."
            )
        else:
            message = (
                f"Sorry, we don’t carry {category}s right now. "
                "But I’d be happy to show you some other products you might like."
            )

        return {
            "message": message,
            "results": suggestions
        }

    # 4️⃣ Filter products
    results = filter_products(
        products,
        max_price=max_price,
        category=category
    )

    # 5️⃣ Fallback: cheapest (valid category, budget too low)
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
