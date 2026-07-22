"""
Test dashboard and analytics endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User
from app.core.security import get_password_hash


@pytest.fixture
def dashboard_user(db_session: Session) -> User:
    """Create a user with dashboard read permissions for testing."""
    role = Role(
        name="Analyst",
        permissions={
            "dashboard": ["read"]
        }
    )
    db_session.add(role)
    db_session.commit()

    user = User(
        email="analyst@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="Data",
        last_name="Analyst",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def dashboard_token(client: TestClient, dashboard_user: User) -> str:
    """Get JWT token for the dashboard analyst."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "analyst@transitops.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


# ============================================================
# ENDPOINT TESTS
# ============================================================

def test_get_dashboard_overview(client: TestClient, dashboard_token: str):
    response = client.get(
        "/api/v1/dashboard/overview",
        headers={"Authorization": f"Bearer {dashboard_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    data = response.json()["data"]
    assert "fleet" in data
    assert "drivers" in data
    assert "trips" in data
    assert "financial" in data


def test_get_fleet_analytics(client: TestClient, dashboard_token: str):
    response = client.get(
        "/api/v1/dashboard/fleet",
        headers={"Authorization": f"Bearer {dashboard_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    data = response.json()["data"]
    assert "total_vehicles" in data


def test_get_trip_analytics(client: TestClient, dashboard_token: str):
    response = client.get(
        "/api/v1/dashboard/trips",
        headers={"Authorization": f"Bearer {dashboard_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    data = response.json()["data"]
    assert "total_trips" in data


def test_get_maintenance_analytics(client: TestClient, dashboard_token: str):
    response = client.get(
        "/api/v1/dashboard/maintenance",
        headers={"Authorization": f"Bearer {dashboard_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    data = response.json()["data"]
    assert "pending_maintenance" in data


def test_get_fuel_analytics(client: TestClient, dashboard_token: str):
    response = client.get(
        "/api/v1/dashboard/fuel",
        headers={"Authorization": f"Bearer {dashboard_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    data = response.json()["data"]
    assert "total_fuel_cost" in data


def test_get_expense_analytics(client: TestClient, dashboard_token: str):
    response = client.get(
        "/api/v1/dashboard/expenses",
        headers={"Authorization": f"Bearer {dashboard_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    data = response.json()["data"]
    assert "total_expenses" in data


def test_get_financial_summary(client: TestClient, dashboard_token: str):
    response = client.get(
        "/api/v1/dashboard/financial-summary",
        headers={"Authorization": f"Bearer {dashboard_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    data = response.json()["data"]
    assert "total_operational_cost" in data


def test_get_dashboard_alerts(client: TestClient, dashboard_token: str):
    response = client.get(
        "/api/v1/dashboard/alerts",
        headers={"Authorization": f"Bearer {dashboard_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    data = response.json()["data"]
    assert "maintenance_due" in data
    assert "licenses_expiring" in data
