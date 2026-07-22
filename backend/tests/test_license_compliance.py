import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.user import User
from app.core.security import get_password_hash

@pytest.fixture
def dashboard_manager_user(db_session: Session) -> User:
    role = Role(
        name="License Dash Manager",
        permissions={
            "dashboard": ["read"]
        }
    )
    db_session.add(role)
    db_session.commit()

    user = User(
        email="licensedash@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="License",
        last_name="Manager",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def dashboard_manager_token(client: TestClient, dashboard_manager_user: User) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "licensedash@transitops.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]

def test_license_summary(client: TestClient, dashboard_manager_token: str):
    response = client.get("/api/v1/license-compliance/summary", headers={"Authorization": f"Bearer {dashboard_manager_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "total_drivers" in data
    assert "valid_licenses" in data

def test_license_compliance_list(client: TestClient, dashboard_manager_token: str):
    response = client.get("/api/v1/license-compliance", headers={"Authorization": f"Bearer {dashboard_manager_token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data

def test_license_compliance_export_csv(client: TestClient, dashboard_manager_token: str):
    response = client.get("/api/v1/license-compliance/export/csv", headers={"Authorization": f"Bearer {dashboard_manager_token}"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"

def test_license_compliance_export_pdf(client: TestClient, dashboard_manager_token: str):
    response = client.get("/api/v1/license-compliance/export/pdf", headers={"Authorization": f"Bearer {dashboard_manager_token}"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
