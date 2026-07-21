"""
Tests for Technician Workload Management endpoints.
"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest
from app.models.role import Role
from app.models.user import User
from app.core.security import get_password_hash

@pytest.fixture
def manager_token(client: TestClient, db_session: Session) -> str:
    role = Role(name="Manager", permissions={"maintenance": ["read", "update"]})
    db_session.add(role)
    db_session.commit()
    user = User(email="mgr@test.com", password_hash=get_password_hash("pass"), first_name="A", last_name="B", role_id=role.id)
    db_session.add(user)
    db_session.commit()
    resp = client.post("/api/v1/auth/login", json={"email": "mgr@test.com", "password": "pass"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}

def test_get_technicians_unauthorized(client: TestClient):
    """Test accessing technicians without token."""
    response = client.get("/api/v1/maintenance/technicians")
    assert response.status_code in [401, 403]

def test_get_technicians(client: TestClient, manager_token: dict):
    """Test getting all technicians."""
    response = client.get("/api/v1/maintenance/technicians", headers=manager_token)
    print("DEBUG 422:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert isinstance(data["data"], list)

def test_get_technicians_summary(client: TestClient, manager_token: dict):
    """Test getting technician summary."""
    response = client.get("/api/v1/maintenance/technicians/summary", headers=manager_token)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_technicians" in data["data"]
    assert "overloaded_technicians" in data["data"]

def test_search_technicians(client: TestClient, manager_token: dict):
    """Test searching technicians."""
    response = client.get("/api/v1/maintenance/technicians/search?q=Mike", headers=manager_token)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_filter_technicians(client: TestClient, manager_token: dict):
    """Test filtering technicians."""
    response = client.get("/api/v1/maintenance/technicians/filter?status=Available", headers=manager_token)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_export_technicians_csv(client: TestClient, manager_token: dict):
    """Test CSV export."""
    response = client.get("/api/v1/maintenance/technicians/export?format=csv", headers=manager_token)
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "ID,Name,Assigned Vehicles" in response.text
