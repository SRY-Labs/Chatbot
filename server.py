from fastapi import FastAPI
from pydantic import BaseModel
from core.data_loader import load_products
from core.agent import handle_user_query

app = FastAPI(title="Robert Allen Design Chatbot API")

products = load_products()

class ChatRequest(BaseModel):
    query: str

class Product(BaseModel):
    product_name: str
    price_usd: int
    product_url: str

class ChatResponse(BaseModel):
    message: str
    results: list[Product]

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    response = handle_user_query(request.query, products)

    return ChatResponse(
        message=response["message"],
        results=[
            Product(
                product_name=p["product_name"],
                price_usd=int(p["price_usd"]),
                product_url=p["product_url"]
            )
            for p in response["results"]
        ]
    )
