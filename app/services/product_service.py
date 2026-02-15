from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.product import Product
from app.schemas.product import ProductCreate

def create_product(db: Session, payload: ProductCreate) -> Product:
    p = Product(**payload.model_dump())
    db.add(p)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Product name already exists")
    db.refresh(p)
    return p

def list_products(db: Session, limit: int, offset: int) -> tuple[int, list[Product]]:
    total = db.execute(select(func.count(Product.id))).scalar_one()
    items = db.execute(
        select(Product)
        .order_by(Product.id.desc())
        .limit(limit)
        .offset(offset)
    ).scalars().all()
    return total, items

def search_products(db: Session, name_contains: str, limit: int, offset: int) -> tuple[int, list[Product]]:
    pattern = f"%{name_contains}%"

    base_where = Product.name.ilike(pattern)

    total = db.execute(
        select(func.count(Product.id)).where(base_where)
    ).scalar_one()

    items = db.execute(
        select(Product)
        .where(base_where)
        .order_by(Product.id.desc())
        .limit(limit)
        .offset(offset)
    ).scalars().all()

    return total, items

def search_all_products(db: Session, name_contains: str) -> list[Product]:
    pattern = f"%{name_contains}%"
    return db.execute(
        select(Product)
        .where(Product.name.ilike(pattern))   # case-insensitive (Postgres)
        .order_by(Product.id.desc())
    ).scalars().all()