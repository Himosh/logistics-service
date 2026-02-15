from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductOut, ProductListResponse
from app.services.product_service import create_product as create_product_svc, list_products as list_products_svc, search_all_products, search_products as search_products_svc
from app.services.product_service import search_all_products as search_all_products_svc

router = APIRouter(prefix="/products", tags=["products"])

@router.post("", response_model=ProductOut, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    return create_product_svc(db, payload)

@router.get("", response_model=ProductListResponse)
def list_products(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    total, items = list_products_svc(db, limit, offset)
    return {"total": total, "limit": limit, "offset": offset, "items": items}

@router.get("/search", response_model=ProductListResponse)
def search_products(
    db: Session = Depends(get_db),
    q: str | None = Query(None, min_length=1, description="Name contains (case-insensitive). Optional."),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    if not q:
        total, items = list_products_svc(db, limit, offset)
    else:
        total, items = search_products_svc(db, q, limit, offset)

    return {"total": total, "limit": limit, "offset": offset, "items": items}

@router.get("/by-name", response_model=list[ProductOut])
def get_products_by_name(
    db: Session = Depends(get_db),
    name: str | None = Query(None, description="Name contains (case-insensitive). Optional."),
):
    name = (name or "").strip()
    if not name:
        # If name is missing/empty, return all products (no pagination)
        return db.execute(select(Product).order_by(Product.id.desc())).scalars().all()

    return search_all_products_svc(db, name)