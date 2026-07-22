import pytest
from uuid import uuid4

def test_get_purchase_orders(client, auth_headers):
    response = client.get("/api/v1/purchase-orders/", headers=auth_headers)
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_purchase_order_summary(client, auth_headers):
    response = client.get("/api/v1/purchase-orders/summary", headers=auth_headers)
    assert response.status_code == 200
    assert "total_orders" in response.json()["data"]

def test_search_purchase_orders(client, auth_headers):
    response = client.get("/api/v1/purchase-orders/search?query=PO-", headers=auth_headers)
    assert response.status_code == 200
    assert "data" in response.json()

def test_filter_purchase_orders(client, auth_headers):
    response = client.get("/api/v1/purchase-orders/filter?status=Processing", headers=auth_headers)
    assert response.status_code == 200
    assert "data" in response.json()
