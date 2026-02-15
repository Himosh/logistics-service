from fastapi import APIRouter, Depends
from fastapi.params import Query
from sqlalchemy.orm import Session
from datetime import date

from app.api.deps import get_db
from app.models.order import OrderStatus
from app.schemas.order import OrderCreate, OrderListResponse, OrderOut, OrderStatusUpdate
from app.services.order_service import create_order, get_order, list_orders, update_order_status
from app.services.order_service import filter_orders_svc

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("", response_model=OrderOut, status_code=201)
def create_order_endpoint(payload: OrderCreate, db: Session = Depends(get_db)):
    return create_order(db, payload)

@router.get("/{order_id}", response_model=OrderOut)
def get_order_endpoint(order_id: int, db: Session = Depends(get_db)):
    return get_order(db, order_id)

@router.patch("/{order_id}/status", response_model=OrderOut)
def update_status_endpoint(order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db)):
    return update_order_status(db, order_id, payload.status)

@router.get("", response_model=OrderListResponse)
def list_orders_endpoint(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    total, items = list_orders(db, limit, offset)
    return {"total": total, "limit": limit, "offset": offset, "items": items}

@router.get("/search", response_model=OrderListResponse)
def search_orders(
    db: Session = Depends(get_db),
    product_name: str | None = Query(None, min_length=1, description="Product name contains (case-insensitive)"),
    status: OrderStatus | None = Query(None),
    date_from: date | None = Query(None, description="YYYY-MM-DD"),
    date_to: date | None = Query(None, description="YYYY-MM-DD"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    total, items = filter_orders_svc(db, product_name, status, date_from, date_to, limit, offset)
    return {"total": total, "limit": limit, "offset": offset, "items": items}