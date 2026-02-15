from sqlalchemy import func, select
from datetime import date, datetime, time, timedelta
from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException

from app.models.product import Product
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.schemas.order import OrderCreate

ALLOWED_TRANSITIONS = {
    OrderStatus.Pending: {OrderStatus.Shipped, OrderStatus.Cancelled},
    OrderStatus.Shipped: set(),
    OrderStatus.Cancelled: set(),
}

def create_order(db: Session, payload: OrderCreate) -> Order:
    requested = sorted(payload.items, key=lambda x: x.product_id)
    product_ids = [i.product_id for i in requested]

    with db.begin():
        products = db.execute(
            select(Product)
            .where(Product.id.in_(product_ids))
            .with_for_update()
        ).scalars().all()

        found = {p.id: p for p in products}
        missing = [pid for pid in product_ids if pid not in found]
        if missing:
            raise HTTPException(status_code=404, detail=f"Products not found: {missing}")

        for item in requested:
            p = found[item.product_id]
            if p.stock_quantity < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product_id={p.id}. Available={p.stock_quantity}, requested={item.quantity}"
                )

        order = Order(status=OrderStatus.Pending)
        db.add(order)
        db.flush()  # assign order.id

        for item in requested:
            p = found[item.product_id]
            p.stock_quantity -= item.quantity

            db.add(OrderItem(
                order_id=order.id,
                product_id=p.id,
                quantity_ordered=item.quantity,
                price_at_time_of_order=float(p.price),
            ))

        db.flush()

    return get_order(db, order.id)

def get_order(db: Session, order_id: int) -> Order:
    q = (
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product)
        )
    )
    order = db.execute(q).scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


def update_order_status(db: Session, order_id: int, new_status: OrderStatus) -> Order:
    with db.begin():
        order = db.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if new_status == order.status:
            pass
        else:
            allowed = ALLOWED_TRANSITIONS.get(order.status, set())
            if new_status not in allowed:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status transition: {order.status} -> {new_status}",
                )
            order.status = new_status
            db.add(order)

    return get_order(db, order_id)


def list_orders(db: Session, limit: int, offset: int):
    total = db.execute(select(func.count(Order.id))).scalar_one()

    q = (
        select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.product)
        )
        .order_by(Order.created_at.desc(), Order.id.desc())
        .limit(limit)
        .offset(offset)
    )
    items = db.execute(q).scalars().all()
    return total, items

def filter_orders(
    db: Session,
    product_name_contains: str | None,
    status: OrderStatus | None,
    date_from: date | None,
    date_to: date | None,
    limit: int,
    offset: int,
) -> tuple[int, list[Order]]:
    conditions = []

    if status:
        conditions.append(Order.status == status)

    if date_from:
        dt_from = datetime.combine(date_from, time.min)
        conditions.append(Order.created_at >= dt_from)

    if date_to:
        dt_to_excl = datetime.combine(date_to + timedelta(days=1), time.min)
        conditions.append(Order.created_at < dt_to_excl)

    # If filtering by product name, join and paginate by distinct Order IDs
    if product_name_contains:
        pattern = f"%{product_name_contains}%"
        conditions.append(Product.name.ilike(pattern))

        total_stmt = (
            select(func.count(func.distinct(Order.id)))
            .select_from(Order)
            .join(Order.items)
            .join(OrderItem.product)
        )
        if conditions:
            total_stmt = total_stmt.where(*conditions)

        total = db.execute(total_stmt).scalar_one()

        id_stmt = (
            select(Order.id, Order.created_at)
            .select_from(Order)
            .join(Order.items)
            .join(OrderItem.product)
            .group_by(Order.id, Order.created_at)
            .order_by(Order.created_at.desc(), Order.id.desc())
            .limit(limit)
            .offset(offset)
        )
        if conditions:
            id_stmt = id_stmt.where(*conditions)

        id_rows = db.execute(id_stmt).all()
        order_ids = [r[0] for r in id_rows]
        if not order_ids:
            return total, []

        orders = db.execute(
            select(Order)
            .where(Order.id.in_(order_ids))
            .options(selectinload(Order.items).selectinload(OrderItem.product))
        ).scalars().all()

        order_map = {o.id: o for o in orders}
        ordered = [order_map[oid] for oid in order_ids if oid in order_map]
        return total, ordered

    # Otherwise no join needed
    total_stmt = select(func.count(Order.id))
    if conditions:
        total_stmt = total_stmt.where(*conditions)
    total = db.execute(total_stmt).scalar_one()

    items_stmt = (
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .order_by(Order.created_at.desc(), Order.id.desc())
        .limit(limit)
        .offset(offset)
    )
    if conditions:
        items_stmt = items_stmt.where(*conditions)

    items = db.execute(items_stmt).scalars().all()
    return total, items