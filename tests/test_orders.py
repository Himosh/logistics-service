from app.models.product import Product

def seed_product(db, name="A", price=10.0, stock=5):
    p = Product(name=name, price=price, stock_quantity=stock)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

def test_create_order_reduces_stock(client, db_session):
    p1 = seed_product(db_session, name="Rice", price=100.0, stock=10)

    resp = client.post("/orders", json={"items": [{"product_id": p1.id, "quantity": 3}]})
    assert resp.status_code == 201, resp.text
    order = resp.json()
    assert order["status"] == "Pending"
    assert order["items"][0]["quantity_ordered"] == 3

    db_session.refresh(p1)
    assert p1.stock_quantity == 7

def test_list_orders_includes_product_name(client, db_session):
    p1 = seed_product(db_session, name="Sugar", price=50.0, stock=10)

    create = client.post("/orders", json={"items": [{"product_id": p1.id, "quantity": 2}]})
    assert create.status_code == 201, create.text

    r_list = client.get("/orders?limit=10&offset=0")
    assert r_list.status_code == 200, r_list.text
    data = r_list.json()

    assert "total" in data and "items" in data
    assert data["total"] >= 1
    assert len(data["items"]) >= 1

    first_item = data["items"][0]["items"][0]
    assert first_item["product_id"] == p1.id
    assert first_item["product_name"] == "Sugar"
