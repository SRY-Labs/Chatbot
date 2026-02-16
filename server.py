from fastapi import FastAPI
from pydantic import BaseModel
import re

from core.data_loader import load_products
from core.agent_tools import filter_products, get_cheapest_product

app = FastAPI(title="Robert Allen Design Chatbot API")

# Load once at startup
products = load_products()

# ---------- Models ----------

class ChatRequest(BaseModel):
    query: str

class Product(BaseModel):
    product_name: str
    price_usd: int
    product_url: str

class ChatResponse(BaseModel):
    message: str
    results: list[Product]

# ---------- Endpoint ----------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    user_query = request.query.lower()

    # Detect max price
    max_price = None
    match = re.search(r"under\s+(\d+)", user_query)
    if match:
        max_price = int(match.group(1))

    # Detect category
    category = "sofa" if "sofa" in user_query else None

    results = filter_products(
        products,
        max_price=max_price,
        category=category
    )

    # Fallback
    if not results and max_price:
        cheapest = get_cheapest_product(products, category=category)

        if cheapest:
            return ChatResponse(
                message="No sofas found under your budget. Here’s the most affordable option:",
                results=[Product(
                    product_name=cheapest["product_name"],
                    price_usd=int(cheapest["price_usd"]),
                    product_url=cheapest["product_url"]
                )]
            )

        return ChatResponse(
            message="I couldn’t find any sofa options right now.",
            results=[]
        )

    return ChatResponse(
        message="Here are some options:",
        results=[
            Product(
                product_name=p["product_name"],
                price_usd=int(p["price_usd"]),
                product_url=p["product_url"]
            )
            for p in results
        ]
    )
