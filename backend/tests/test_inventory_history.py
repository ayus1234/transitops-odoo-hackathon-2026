import pytest
from uuid import uuid4

def test_get_inventory_history(client, auth_headers):
    response = client.get("/api/v1/inventory/history", headers=auth_headers)
    assert response.status_code == 200
    assert "data" in response.json()

def test_search_inventory_history(client, auth_headers):
    response = client.get("/api/v1/inventory/history/search?query=restock", headers=auth_headers)
    assert response.status_code == 200
    assert "data" in response.json()

def test_filter_inventory_history(client, auth_headers):
    # Dummy UUID for testing filter format
    dummy_id = str(uuid4())
    response = client.get(f"/api/v1/inventory/history/filter?part_id={dummy_id}", headers=auth_headers)
    assert response.status_code == 200
    assert "data" in response.json()
