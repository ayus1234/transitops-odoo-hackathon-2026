import pytest
from uuid import uuid4

def test_get_procurement_requests(client, auth_headers):
    response = client.get("/api/v1/procurement/requests", headers=auth_headers)
    assert response.status_code == 200
    assert "data" in response.json()

def test_get_procurement_summary(client, auth_headers):
    response = client.get("/api/v1/procurement/summary", headers=auth_headers)
    assert response.status_code == 200
    assert "total_requests" in response.json()["data"]

def test_search_procurement(client, auth_headers):
    response = client.get("/api/v1/procurement/search?query=PR-", headers=auth_headers)
    assert response.status_code == 200
    assert "data" in response.json()

def test_filter_procurement(client, auth_headers):
    response = client.get("/api/v1/procurement/filter?status=Draft", headers=auth_headers)
    assert response.status_code == 200
    assert "data" in response.json()
