from sqlalchemy import CheckConstraint, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)

    quantity_ordered: Mapped[int] = mapped_column()
    price_at_time_of_order: Mapped[float] = mapped_column(Numeric(10, 2))

    order = relationship("Order", back_populates="items")
    product = relationship("Product")

    __table_args__ = (
        CheckConstraint("quantity_ordered > 0", name="ck_order_items_qty_positive"),
        CheckConstraint("price_at_time_of_order >= 0", name="ck_order_items_price_non_negative"),
    )

    @property
    def product_name(self) -> str | None:
        return self.product.name if self.product else None
