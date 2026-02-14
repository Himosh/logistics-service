from fastapi import FastAPI
from app.api.routes import products, orders

app = FastAPI(title="Logistics Service")

app.include_router(products.router)
app.include_router(orders.router)

@app.get("/health")
def health():
    return {"status": "ok"}
