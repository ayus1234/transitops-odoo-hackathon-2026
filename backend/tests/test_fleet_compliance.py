import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.user import User
from app.core.security import get_password_hash

@pytest.fixture
def dashboard_manager_user_fc(db_session: Session) -> User:
    role = Role(
        name="Fleet Dash Manager",
        permissions={
            "dashboard": ["read"]
        }
    )
    db_session.add(role)
    db_session.commit()

    user = User(
        email="fleetdash@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="Fleet",
        last_name="Manager",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def dashboard_manager_token_fc(client: TestClient, dashboard_manager_user_fc: User) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "fleetdash@transitops.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]

def test_fleet_summary(client: TestClient, dashboard_manager_token_fc: str):
    response = client.get("/api/v1/fleet-compliance/summary", headers={"Authorization": f"Bearer {dashboard_manager_token_fc}"})
    assert response.status_code == 200
    data = response.json()
    assert "fleet_compliance_score" in data

def test_fleet_analytics(client: TestClient, dashboard_manager_token_fc: str):
    response = client.get("/api/v1/fleet-compliance/analytics", headers={"Authorization": f"Bearer {dashboard_manager_token_fc}"})
    assert response.status_code == 200
    data = response.json()
    assert "weekly_trends" in data

def test_fleet_export_csv(client: TestClient, dashboard_manager_token_fc: str):
    response = client.get("/api/v1/fleet-compliance/export/csv", headers={"Authorization": f"Bearer {dashboard_manager_token_fc}"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

def test_fleet_export_pdf(client: TestClient, dashboard_manager_token_fc: str):
    response = client.get("/api/v1/fleet-compliance/export/pdf", headers={"Authorization": f"Bearer {dashboard_manager_token_fc}"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
