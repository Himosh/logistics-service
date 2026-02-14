from sqlalchemy import CheckConstraint, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    stock_quantity: Mapped[int] = mapped_column(default=0)

    __table_args__ = (
        CheckConstraint("stock_quantity >= 0", name="ck_products_stock_non_negative"),
        CheckConstraint("price >= 0", name="ck_products_price_non_negative"),
    )
