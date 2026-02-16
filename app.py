from core.data_loader import load_products
from core.agent_tools import filter_products, get_cheapest_product
from core.formatter import format_response
import re

products = load_products()

print(" Robert Allen Design Chatbot")
print("Type 'exit' to quit.\n")

while True:
    user_query = input("You: ").strip()

    if user_query.lower() in {"exit", "quit"}:
        print("👋 Goodbye!")
        break

    # 🔹 Detect max price (e.g. "under 1500")
    max_price = None
    match = re.search(r"under\s+(\d+)", user_query.lower())
    if match:
        max_price = int(match.group(1))

    # 🔹 Detect category
    category = "sofa" if "sofa" in user_query.lower() else None

    results = filter_products(
        products,
        max_price=max_price,
        category=category
    )

    # 🔹 Fallback: suggest cheapest option if nothing matches
    if not results and max_price:
        cheapest = get_cheapest_product(products, category=category)

        if cheapest:
            response = (
                f"I don’t have sofas under ${max_price}. "
                f"The most affordable option is {cheapest['product_name']} "
                f"at ${int(cheapest['price_usd'])}. "
                f"You can view it here: {cheapest['product_url']}"
            )
        else:
            response = "I couldn’t find any sofa options right now."
    else:
        response = format_response(results)

    print("\nBot:", response, "\n")
