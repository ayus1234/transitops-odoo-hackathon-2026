"""
Tests for Maintenance Tasks endpoints.
"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest
from app.models.role import Role
from app.models.user import User
from app.core.security import get_password_hash
import uuid

@pytest.fixture
def manager_token(client: TestClient, db_session: Session) -> str:
    role = Role(name="Manager", permissions={"maintenance": ["read", "update"]})
    db_session.add(role)
    db_session.commit()
    user = User(email="mgr2@test.com", password_hash=get_password_hash("pass"), first_name="A", last_name="B", role_id=role.id)
    db_session.add(user)
    db_session.commit()
    resp = client.post("/api/v1/auth/login", json={"email": "mgr2@test.com", "password": "pass"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}

def test_get_tasks_unauthorized(client: TestClient):
    """Test accessing tasks without token."""
    response = client.get("/api/v1/maintenance/tasks")
    assert response.status_code in [401, 403]

def test_get_tasks(client: TestClient, manager_token: dict):
    """Test getting all tasks."""
    response = client.get("/api/v1/maintenance/tasks", headers=manager_token)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)

def test_get_tasks_summary(client: TestClient, manager_token: dict):
    """Test getting task summary."""
    response = client.get("/api/v1/maintenance/tasks/summary", headers=manager_token)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_tasks" in data["data"]
    assert "overdue_tasks" in data["data"]

def test_search_tasks(client: TestClient, manager_token: dict):
    """Test searching tasks."""
    response = client.get("/api/v1/maintenance/tasks/search?q=Repair", headers=manager_token)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_filter_tasks(client: TestClient, manager_token: dict):
    """Test filtering tasks."""
    response = client.get("/api/v1/maintenance/tasks/filter?status=Pending", headers=manager_token)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_export_tasks_csv(client: TestClient, manager_token: dict):
    """Test CSV export."""
    response = client.get("/api/v1/maintenance/tasks/export?format=csv", headers=manager_token)
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "Task ID,Vehicle Name" in response.text

def test_assign_technician_not_found(client: TestClient, manager_token: dict):
    """Test assigning technician to non-existent task."""
    fake_id = str(uuid.uuid4())
    response = client.post(
        f"/api/v1/maintenance/tasks/{fake_id}/assign",
        headers=manager_token,
        json={"technician_name": "Test Tech"}
    )
    # The service returns SuccessResponse(success=False) for ValueError
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()
