import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.user import User
from app.core.security import get_password_hash

@pytest.fixture
def dashboard_manager_user_si(db_session: Session) -> User:
    role = Role(
        name="Safety Dash Manager",
        permissions={
            "dashboard": ["read"]
        }
    )
    db_session.add(role)
    db_session.commit()

    user = User(
        email="safetydash@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="Safety",
        last_name="Manager",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def dashboard_manager_token_si(client: TestClient, dashboard_manager_user_si: User) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "safetydash@transitops.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]

def test_safety_summary(client: TestClient, dashboard_manager_token_si: str):
    response = client.get("/api/v1/safety-insights/summary", headers={"Authorization": f"Bearer {dashboard_manager_token_si}"})
    assert response.status_code == 200
    data = response.json()
    assert "fleet_safety_score" in data

def test_safety_rankings(client: TestClient, dashboard_manager_token_si: str):
    response = client.get("/api/v1/safety-insights/rankings", headers={"Authorization": f"Bearer {dashboard_manager_token_si}"})
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data

def test_safety_alerts(client: TestClient, dashboard_manager_token_si: str):
    response = client.get("/api/v1/safety-insights/alerts", headers={"Authorization": f"Bearer {dashboard_manager_token_si}"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data

def test_safety_export_csv(client: TestClient, dashboard_manager_token_si: str):
    response = client.get("/api/v1/safety-insights/export/csv", headers={"Authorization": f"Bearer {dashboard_manager_token_si}"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

def test_safety_export_pdf(client: TestClient, dashboard_manager_token_si: str):
    response = client.get("/api/v1/safety-insights/export/pdf", headers={"Authorization": f"Bearer {dashboard_manager_token_si}"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
