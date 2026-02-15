from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from app.models.order import OrderStatus

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)

class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(min_length=1)

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    product_name: str | None
    quantity_ordered: int
    price_at_time_of_order: float

    model_config = {"from_attributes": True}

class OrderOut(BaseModel):
    id: int
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemOut]

    model_config = {"from_attributes": True}
    
class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class OrderListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[OrderOut]