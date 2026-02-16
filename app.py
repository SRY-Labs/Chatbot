from core.data_loader import load_products
from core.agent import handle_user_query
from core.formatter import format_response

products = load_products()

print(" Robert Allen Design Chatbot")
print("Type 'exit' to quit.\n")

while True:
    user_query = input("You: ").strip()

    if user_query.lower() in {"exit", "quit"}:
        print("👋 Goodbye!")
        break

    response = handle_user_query(user_query, products)
    print("\nBot:", format_response(response["results"], response["message"]), "\n")
