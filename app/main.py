from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import products, orders

app = FastAPI(title="Logistics Service")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(orders.router)

@app.get("/health")
def health():
    return {"status": "ok"}
