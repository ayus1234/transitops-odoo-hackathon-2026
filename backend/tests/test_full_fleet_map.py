import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

def test_get_full_fleet_map(client: TestClient, admin_token_headers: dict):
    response = client.get("/api/v1/fleet-map/full", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "vehicles" in data
    assert "drivers" in data
    assert "trips" in data
    assert "bounds" in data

def test_get_vehicle_markers(client: TestClient, admin_token_headers: dict):
    response = client.get("/api/v1/fleet-map/vehicles", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_driver_markers(client: TestClient, admin_token_headers: dict):
    response = client.get("/api/v1/fleet-map/drivers", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_active_trips(client: TestClient, admin_token_headers: dict):
    response = client.get("/api/v1/fleet-map/trips", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_search_fleet_map(client: TestClient, admin_token_headers: dict):
    response = client.get("/api/v1/fleet-map/search?q=truck", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "vehicles" in data

def test_filter_fleet_map(client: TestClient, admin_token_headers: dict):
    response = client.get("/api/v1/fleet-map/filter?vehicle_status=Available", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "vehicles" in data
    
def test_get_bounds(client: TestClient, admin_token_headers: dict):
    response = client.get("/api/v1/fleet-map/bounds", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "min_lat" in data

def test_unauthorized_access(client: TestClient):
    response = client.get("/api/v1/fleet-map/full")
    assert response.status_code in (401, 403)
