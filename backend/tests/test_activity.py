import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from app.main import app
from app.api.deps import get_current_user
from app.models.activity import ActivityLog, ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.models.user import User
from app.models.role import Role
from app.schemas.activity import ActivityCreate
from app.services.activity_service import activity_service

@pytest.fixture
def admin_user(db_session: Session):
    role = Role(id=uuid4(), name="Administrator")
    db_session.add(role)
    user = User(id=uuid4(), email="admin@test.com", role_id=role.id, first_name="A", last_name="B", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def driver_user(db_session: Session):
    role = Role(id=uuid4(), name="Driver")
    db_session.add(role)
    user = User(id=uuid4(), email="driver@test.com", role_id=role.id, first_name="D", last_name="C", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    return user

def create_mock_activity(db: Session, user_id=None, module=ModuleEnum.VEHICLE):
    act = ActivityCreate(
        module=module,
        activity_type=ActivityTypeEnum.CREATED,
        title="Test Activity",
        description="A mock activity for testing",
        severity=SeverityEnum.INFO,
        status="Success",
        user_id=user_id or uuid4()
    )
    return activity_service.log_activity(db, act)


def test_create_manual_activity(client: TestClient, admin_user: User):
    app.dependency_overrides[get_current_user] = lambda: admin_user
    
    response = client.post(
        "/api/v1/activity",
        json={
            "module": "Dashboard",
            "activity_type": "System",
            "title": "Manual Test",
            "description": "System check",
            "severity": "Info",
            "status": "Success"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Manual Test"
    assert data["module"] == "Dashboard"
    
    app.dependency_overrides.clear()


def test_create_manual_activity_unauthorized(client: TestClient, driver_user: User):
    app.dependency_overrides[get_current_user] = lambda: driver_user
    
    response = client.post(
        "/api/v1/activity",
        json={
            "module": "Dashboard",
            "activity_type": "System",
            "title": "Manual Test"
        }
    )
    assert response.status_code in [403, 401]
    
    app.dependency_overrides.clear()


def test_get_activities_paginated(client: TestClient, admin_user: User, db_session: Session):
    app.dependency_overrides[get_current_user] = lambda: admin_user
    
    create_mock_activity(db_session, user_id=admin_user.id, module=ModuleEnum.DASHBOARD)
    create_mock_activity(db_session, user_id=admin_user.id, module=ModuleEnum.VEHICLE)

    response = client.get("/api/v1/activity?limit=10&skip=0")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 2
    
    app.dependency_overrides.clear()


def test_get_activities_filtered(client: TestClient, admin_user: User, db_session: Session):
    app.dependency_overrides[get_current_user] = lambda: admin_user
    
    create_mock_activity(db_session, user_id=admin_user.id, module=ModuleEnum.DASHBOARD)
    create_mock_activity(db_session, user_id=admin_user.id, module=ModuleEnum.EXPENSE)

    response = client.get("/api/v1/activity?module=Dashboard")
    assert response.status_code == 200
    data = response.json()
    assert all(item["module"] == "Dashboard" for item in data["items"])
    
    app.dependency_overrides.clear()


def test_get_activities_search(client: TestClient, admin_user: User, db_session: Session):
    app.dependency_overrides[get_current_user] = lambda: admin_user
    
    act = ActivityCreate(
        module=ModuleEnum.DASHBOARD,
        activity_type=ActivityTypeEnum.SYSTEM,
        title="Unique Search Title X1Y2Z3",
        severity=SeverityEnum.INFO,
        user_id=admin_user.id
    )
    activity_service.log_activity(db_session, act)

    response = client.get("/api/v1/activity?search=X1Y2Z3")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Unique Search Title X1Y2Z3"
    
    app.dependency_overrides.clear()


def test_get_statistics(client: TestClient, admin_user: User, db_session: Session):
    app.dependency_overrides[get_current_user] = lambda: admin_user
    
    create_mock_activity(db_session, user_id=admin_user.id)
    
    response = client.get("/api/v1/activity/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "total_activities" in data
    assert "activities_by_module" in data
    
    app.dependency_overrides.clear()


def test_export_csv(client: TestClient, admin_user: User, db_session: Session):
    app.dependency_overrides[get_current_user] = lambda: admin_user
    
    create_mock_activity(db_session, user_id=admin_user.id)
    response = client.get("/api/v1/activity/export?format=csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "ID,Date,Module" in response.text
    
    app.dependency_overrides.clear()


def test_export_pdf(client: TestClient, admin_user: User, db_session: Session):
    app.dependency_overrides[get_current_user] = lambda: admin_user
    
    create_mock_activity(db_session, user_id=admin_user.id)
    response = client.get("/api/v1/activity/export?format=pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "TRANSITOPS - ENTERPRISE ACTIVITY LOG EXPORT" in response.text
    
    app.dependency_overrides.clear()


def test_get_recent_activities(client: TestClient, admin_user: User, db_session: Session):
    app.dependency_overrides[get_current_user] = lambda: admin_user
    
    for _ in range(6):
        create_mock_activity(db_session, user_id=admin_user.id)
        
    response = client.get("/api/v1/activity/recent?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5
    
    response_10 = client.get("/api/v1/activity/recent?limit=10")
    assert response_10.status_code == 200
    assert len(response_10.json()) >= 6
    
    app.dependency_overrides.clear()
