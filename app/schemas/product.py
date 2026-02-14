from typing import List
from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price: float = Field(ge=0)
    stock_quantity: int = Field(ge=0)

class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    stock_quantity: int

    model_config = {"from_attributes": True}

class ProductListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[ProductOut]