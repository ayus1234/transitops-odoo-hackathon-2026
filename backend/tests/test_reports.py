"""
Test report endpoints and exports.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User
from app.core.security import get_password_hash


@pytest.fixture
def report_user(db_session: Session) -> User:
    """Create a user with report read permissions for testing."""
    role = Role(
        name="Reporter",
        permissions={
            "reports": ["read"]
        }
    )
    db_session.add(role)
    db_session.commit()

    user = User(
        email="reporter@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="Report",
        last_name="Manager",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def report_token(client: TestClient, report_user: User) -> str:
    """Get JWT token for the reporter."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "reporter@transitops.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


# ============================================================
# ENDPOINT TESTS
# ============================================================

def test_get_fleet_report_json(client: TestClient, report_token: str):
    response = client.get(
        "/api/v1/reports/fleet?export_format=json",
        headers={"Authorization": f"Bearer {report_token}"}
    )
    assert response.status_code == 200
    assert response.json()["report_type"] == "Fleet Report"
    assert "data" in response.json()


def test_get_driver_report_csv(client: TestClient, report_token: str):
    response = client.get(
        "/api/v1/reports/drivers?export_format=csv",
        headers={"Authorization": f"Bearer {report_token}"}
    )
    assert response.status_code == 400
    assert "No data available" in response.json()["error"]["message"]


def test_get_trip_report_xlsx(client: TestClient, report_token: str):
    response = client.get(
        "/api/v1/reports/trips?export_format=xlsx",
        headers={"Authorization": f"Bearer {report_token}"}
    )
    assert response.status_code == 400
    assert "No data available" in response.json()["error"]["message"]


def test_get_financial_report_pdf(client: TestClient, report_token: str):
    response = client.get(
        "/api/v1/reports/financial?export_format=pdf",
        headers={"Authorization": f"Bearer {report_token}"}
    )
    assert response.status_code in [200, 400]
    if response.status_code == 400:
        assert "No data available" in response.json()["error"]["message"]


def test_invalid_export_format(client: TestClient, report_token: str):
    response = client.get(
        "/api/v1/reports/fleet?export_format=invalid",
        headers={"Authorization": f"Bearer {report_token}"}
    )
    assert response.status_code == 400
