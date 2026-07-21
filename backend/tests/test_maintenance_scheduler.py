import pytest
from fastapi.testclient import TestClient
from datetime import date, time, timedelta
from app.models.role import Role
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.orm import Session

@pytest.fixture
def fleet_manager_token(client: TestClient, db_session: Session) -> str:
    role = Role(
        name="Fleet Manager",
        permissions={
            "maintenance": ["read", "create", "update", "delete"]
        }
    )
    db_session.add(role)
    db_session.commit()

    user = User(
        email="manager_sched@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="Fleet",
        last_name="Manager",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "manager_sched@transitops.com", "password": "password123"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

def test_get_scheduler_events(client: TestClient, fleet_manager_token: dict):
    response = client.get(
        "/api/v1/maintenance/scheduler",
        headers=fleet_manager_token
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)

def test_get_upcoming_jobs(client: TestClient, fleet_manager_token: dict):
    response = client.get(
        "/api/v1/maintenance/scheduler/upcoming",
        headers=fleet_manager_token
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_scheduler_search(client: TestClient, fleet_manager_token: dict):
    response = client.get(
        "/api/v1/maintenance/scheduler/search?q=oil",
        headers=fleet_manager_token
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
