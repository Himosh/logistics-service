from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.product import ProductCreate, ProductOut, ProductListResponse
from app.services.product_service import create_product as create_product_svc, list_products as list_products_svc

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
