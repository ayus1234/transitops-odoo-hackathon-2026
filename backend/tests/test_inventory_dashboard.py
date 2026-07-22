import pytest
from uuid import uuid4

def test_get_inventory_dashboard(client, auth_headers):
    response = client.get("/api/v1/inventory/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert "total_parts" in data
    assert "inventory_health_score" in data

def test_get_inventory_parts(client, auth_headers):
    response = client.get("/api/v1/inventory/parts", headers=auth_headers)
    assert response.status_code == 200
    assert "data" in response.json()

def test_search_inventory(client, auth_headers):
    response = client.get("/api/v1/inventory/search?query=brake", headers=auth_headers)
    assert response.status_code == 200
    assert "data" in response.json()

def test_filter_inventory(client, auth_headers):
    response = client.get("/api/v1/inventory/filter?status=In Stock", headers=auth_headers)
    assert response.status_code == 200
    assert "data" in response.json()
