import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User
from app.core.security import get_password_hash

@pytest.fixture
def report_admin_user(db_session: Session) -> User:
    """Create a user with admin permissions for testing."""
    role = Role(
        name="Admin",
        permissions={
            "reports": ["read", "write", "execute", "schedule"]
        }
    )
    db_session.add(role)
    db_session.commit()

    user = User(
        email="reportadmin@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="Report",
        last_name="Admin",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def report_admin_token(client: TestClient, report_admin_user: User) -> str:
    """Get JWT token for the admin."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "reportadmin@transitops.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


def test_create_custom_report(client: TestClient, report_admin_token: str):
    response = client.post(
        "/api/v1/custom-reports",
        headers={"Authorization": f"Bearer {report_admin_token}"},
        json={
            "name": "Test Vehicle Report",
            "module": "Vehicles",
            "selected_fields": ["id", "registration_number", "status"],
            "filters": [
                {"field": "status", "operator": "Equals", "value": "Available"}
            ],
            "is_public": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Vehicle Report"
    assert data["module"] == "Vehicles"
    assert "id" in data

def test_get_custom_reports(client: TestClient, report_admin_token: str):
    response = client.get(
        "/api/v1/custom-reports",
        headers={"Authorization": f"Bearer {report_admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

def test_execute_custom_report(client: TestClient, report_admin_token: str):
    # First create a report
    create_response = client.post(
        "/api/v1/custom-reports",
        headers={"Authorization": f"Bearer {report_admin_token}"},
        json={
            "name": "Execute Vehicle Report",
            "module": "Vehicles",
            "selected_fields": ["registration_number", "status"],
        }
    )
    report_id = create_response.json()["id"]

    # Now execute it
    execute_response = client.post(
        f"/api/v1/custom-reports/{report_id}/execute",
        headers={"Authorization": f"Bearer {report_admin_token}"}
    )
    assert execute_response.status_code == 200
    data = execute_response.json()
    assert "columns" in data
    assert "data" in data
    assert "row_count" in data
    assert "execution_time_ms" in data

def test_export_report_csv(client: TestClient, report_admin_token: str):
    create_response = client.post(
        "/api/v1/custom-reports",
        headers={"Authorization": f"Bearer {report_admin_token}"},
        json={
            "name": "Export CSV Report",
            "module": "Vehicles",
            "selected_fields": ["registration_number", "status"],
        }
    )
    report_id = create_response.json()["id"]

    export_response = client.post(
        f"/api/v1/custom-reports/{report_id}/export?format=csv",
        headers={"Authorization": f"Bearer {report_admin_token}"}
    )
    assert export_response.status_code == 200
    assert "text/csv" in export_response.headers.get("content-type")
    
def test_export_report_excel(client: TestClient, report_admin_token: str):
    create_response = client.post(
        "/api/v1/custom-reports",
        headers={"Authorization": f"Bearer {report_admin_token}"},
        json={
            "name": "Export Excel Report",
            "module": "Vehicles",
            "selected_fields": ["registration_number", "status"],
        }
    )
    report_id = create_response.json()["id"]

    export_response = client.post(
        f"/api/v1/custom-reports/{report_id}/export?format=excel",
        headers={"Authorization": f"Bearer {report_admin_token}"}
    )
    assert export_response.status_code == 200
    assert "application/vnd.ms-excel" in export_response.headers.get("content-type")

def test_export_report_pdf(client: TestClient, report_admin_token: str):
    create_response = client.post(
        "/api/v1/custom-reports",
        headers={"Authorization": f"Bearer {report_admin_token}"},
        json={
            "name": "Export PDF Report",
            "module": "Vehicles",
            "selected_fields": ["registration_number", "status"],
        }
    )
    report_id = create_response.json()["id"]

    export_response = client.post(
        f"/api/v1/custom-reports/{report_id}/export?format=pdf",
        headers={"Authorization": f"Bearer {report_admin_token}"}
    )
    assert export_response.status_code == 200
    assert "application/pdf" in export_response.headers.get("content-type")

def test_export_report_json(client: TestClient, report_admin_token: str):
    create_response = client.post(
        "/api/v1/custom-reports",
        headers={"Authorization": f"Bearer {report_admin_token}"},
        json={
            "name": "Export JSON Report",
            "module": "Vehicles",
            "selected_fields": ["registration_number", "status"],
        }
    )
    report_id = create_response.json()["id"]

    export_response = client.post(
        f"/api/v1/custom-reports/{report_id}/export?format=json",
        headers={"Authorization": f"Bearer {report_admin_token}"}
    )
    assert export_response.status_code == 200
    assert "application/json" in export_response.headers.get("content-type")

def test_schedule_report(client: TestClient, report_admin_token: str):
    create_response = client.post(
        "/api/v1/custom-reports",
        headers={"Authorization": f"Bearer {report_admin_token}"},
        json={
            "name": "Scheduled Report",
            "module": "Vehicles",
            "selected_fields": ["registration_number"]
        }
    )
    report_id = create_response.json()["id"]
    
    schedule_response = client.post(
        f"/api/v1/custom-reports/{report_id}/schedule",
        headers={"Authorization": f"Bearer {report_admin_token}"},
        json={
            "frequency": "weekly",
            "cron_expression": "0 0 * * 0",
            "email_recipients": ["test@example.com"]
        }
    )
    assert schedule_response.status_code == 200
    data = schedule_response.json()
    assert data["frequency"] == "weekly"
    assert data["report_id"] == report_id
    assert "test@example.com" in data["email_recipients"]
