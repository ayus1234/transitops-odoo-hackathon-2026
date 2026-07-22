import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

def test_get_tickets(client: TestClient, admin_token_headers: dict):
    response = client.get("/api/v1/help/tickets", headers=admin_token_headers)
    assert response.status_code == 200
    assert "data" in response.json()
    assert isinstance(response.json()["data"], list)


def test_create_ticket(client: TestClient, driver_token_headers: dict):
    data = {
        "title": "My GPS is broken",
        "description": "Please fix my GPS on vehicle 123",
        "module_name": "Vehicles",
        "category": "Bug Report",
        "priority": "High"
    }
    response = client.post("/api/v1/help/tickets", json=data, headers=driver_token_headers)
    assert response.status_code == 201
    res_data = response.json()["data"]
    assert res_data["title"] == "My GPS is broken"
    assert res_data["status"] == "Open"
    assert "ticket_number" in res_data
    return res_data["id"]


def test_driver_cannot_resolve_ticket(client: TestClient, driver_token_headers: dict, admin_token_headers: dict):
    # Driver creates a ticket
    data = {
        "title": "Engine light",
        "description": "Engine light on",
        "module_name": "Maintenance",
        "category": "Bug Report",
        "priority": "Medium"
    }
    response = client.post("/api/v1/help/tickets", json=data, headers=driver_token_headers)
    ticket_id = response.json()["data"]["id"]
    
    # Driver tries to resolve it (should fail 403)
    res_response = client.post(f"/api/v1/help/tickets/{ticket_id}/resolve", params={"resolution_notes": "Fixed"}, headers=driver_token_headers)
    assert res_response.status_code == 403


def test_admin_can_resolve_ticket(client: TestClient, driver_token_headers: dict, admin_token_headers: dict):
    # Driver creates a ticket
    data = {
        "title": "Need new route",
        "description": "Route 5 is blocked",
        "module_name": "Trips",
        "category": "General Inquiry",
        "priority": "Medium"
    }
    response = client.post("/api/v1/help/tickets", json=data, headers=driver_token_headers)
    ticket_id = response.json()["data"]["id"]
    
    # Admin resolves it
    res_response = client.post(f"/api/v1/help/tickets/{ticket_id}/resolve", params={"resolution_notes": "Re-routed"}, headers=admin_token_headers)
    assert res_response.status_code == 200
    assert res_response.json()["data"]["status"] == "Resolved"
    assert res_response.json()["data"]["resolution_notes"] == "Re-routed"


def test_search_tickets(client: TestClient, admin_token_headers: dict):
    response = client.get("/api/v1/help/tickets/search?q=GPS", headers=admin_token_headers)
    assert response.status_code == 200
    # Could be empty depending on DB state, just check structure
    assert "data" in response.json()
