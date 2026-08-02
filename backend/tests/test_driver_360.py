"""
Tests for Driver 360 profile and performance score extensions.
"""
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.role import Role
from app.models.user import User
from app.models.driver import Driver
from app.core.security import get_password_hash


@pytest.fixture
def driver_360_manager(db_session: Session) -> User:
    """Create Fleet Manager for Driver 360 testing."""
    role = Role(
        name="Fleet Manager D360",
        permissions={"drivers": ["read", "create", "update", "delete"]}
    )
    db_session.add(role)
    db_session.commit()

    user = User(
        email="d360_manager@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="Driver",
        last_name="Manager360",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def driver_360_token(client: TestClient, driver_360_manager: User) -> str:
    """Get JWT token for Driver 360 tester."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "d360_manager@transitops.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def driver_360_record(db_session: Session) -> Driver:
    """Create a driver with Driver 360 attributes."""
    role = db_session.query(Role).filter(Role.name == "Driver").first()
    if not role:
        role = Role(name="Driver", permissions={"trips": ["read"]})
        db_session.add(role)
        db_session.commit()

    user = User(
        email="d360_driver@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="John",
        last_name="Doe360",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.flush()

    driver = Driver(
        user_id=user.id,
        license_number="DL-360-TEST-01",
        license_category="HMV",
        license_class="HGV Class 1",
        license_issue_date=date(2020, 1, 1),
        license_expiry_date=date(2028, 1, 1),
        date_of_birth=date(1990, 5, 15),
        blood_group="O+",
        medical_fitness_expiry=date(2027, 6, 30),
        emergency_contact="+919876543210",
        safety_score=Decimal("95.50"),
        efficiency_score=Decimal("92.00"),
        compliance_score=Decimal("98.00"),
        overall_score=Decimal("95.17"),
        status="Available"
    )
    db_session.add(driver)
    db_session.commit()
    db_session.refresh(driver)
    return driver


def test_get_driver_360_profile(
    client: TestClient,
    driver_360_token: str,
    driver_360_record: Driver
):
    """Test GET /drivers/{id}/360 endpoint."""
    response = client.get(
        f"/api/v1/drivers/{driver_360_record.id}/360",
        headers={"Authorization": f"Bearer {driver_360_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "driver" in data
    assert data["driver"]["license_number"] == "DL-360-TEST-01"
    assert data["driver"]["license_class"] == "HGV Class 1"
    assert data["driver"]["blood_group"] == "O+"
    assert float(data["driver"]["safety_score"]) == 95.50
    assert float(data["driver"]["efficiency_score"]) == 92.00
    assert float(data["driver"]["compliance_score"]) == 98.00
    assert data["driver"]["is_license_valid"] is True
    assert data["driver"]["is_medical_valid"] is True


def test_update_driver_360_scores_and_medical(
    client: TestClient,
    driver_360_token: str,
    driver_360_record: Driver
):
    """Test updating Driver 360 scores and medical fitness date."""
    new_medical = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")

    update_data = {
        "efficiency_score": 96.00,
        "compliance_score": 99.00,
        "overall_score": 96.83,
        "medical_fitness_expiry": new_medical,
        "notes": "Annual medical check cleared"
    }

    response = client.put(
        f"/api/v1/drivers/{driver_360_record.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {driver_360_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert float(data["efficiency_score"]) == 96.00
    assert float(data["compliance_score"]) == 99.00
    assert data["medical_fitness_expiry"] == new_medical
    assert data["notes"] == "Annual medical check cleared"


def test_get_driver_performance_metrics(
    client: TestClient,
    driver_360_token: str,
    driver_360_record: Driver
):
    """Test GET /drivers/{id}/performance endpoint."""
    response = client.get(
        f"/api/v1/drivers/{driver_360_record.id}/performance",
        headers={"Authorization": f"Bearer {driver_360_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    perf = data["data"]
    assert perf["driver_id"] == str(driver_360_record.id)
    assert perf["safety_score"] == 95.50
    assert perf["efficiency_score"] == 92.00
    assert perf["compliance_score"] == 98.00
    assert perf["medical_valid"] is True


def test_driver_360_not_found(
    client: TestClient,
    driver_360_token: str
):
    """Test GET /drivers/{id}/360 for non-existent driver returns error."""
    import uuid
    fake_id = uuid.uuid4()

    response = client.get(
        f"/api/v1/drivers/{fake_id}/360",
        headers={"Authorization": f"Bearer {driver_360_token}"}
    )

    assert response.status_code == 400
    assert "not found" in response.json()["error"]["message"].lower()
