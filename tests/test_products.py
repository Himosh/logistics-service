def test_create_product_and_list_with_metadata(client):
    r1 = client.post("/products", json={"name": "P1", "price": 10, "stock_quantity": 5})
    assert r1.status_code == 201, r1.text
    p1 = r1.json()
    assert p1["name"] == "P1"

    r2 = client.post("/products", json={"name": "P2", "price": 20, "stock_quantity": 7})
    assert r2.status_code == 201, r2.text

    r_list = client.get("/products?limit=1&offset=0")
    assert r_list.status_code == 200, r_list.text
    data = r_list.json()

    assert "total" in data and "items" in data and "limit" in data and "offset" in data
    assert data["limit"] == 1
    assert data["offset"] == 0
    assert data["total"] >= 2
    assert len(data["items"]) == 1
