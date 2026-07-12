"""
Test driver endpoints.
"""
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User
from app.models.driver import Driver
from app.core.security import get_password_hash


@pytest.fixture
def driver_role(db_session: Session) -> Role:
    """Create Driver role."""
    role = Role(name="Driver", permissions={"trips": ["read"]})
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture
def fleet_manager_user(db_session: Session) -> User:
    """Create Fleet Manager user for testing."""
    role = Role(
        name="Fleet Manager",
        permissions={"drivers": ["read", "create", "update", "delete"]}
    )
    db_session.add(role)
    db_session.commit()
    
    user = User(
        email="manager@transitops.com",
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
def fleet_manager_token(client: TestClient, fleet_manager_user: User) -> str:
    """Get JWT token for Fleet Manager."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "manager@transitops.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


def test_create_driver_success(
    client: TestClient,
    db_session: Session,
    driver_role: Role,
    fleet_manager_token: str
):
    """Test successful driver creation."""
    # Prepare driver data
    driver_data = {
        "user": {
            "email": "driver1@transitops.com",
            "password": "driver123",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+1234567890"
        },
        "license_number": "DL-123456",
        "license_category": "HMV",
        "license_issue_date": "2020-01-01",
        "license_expiry_date": "2030-12-31",
        "date_of_birth": "1990-05-15",
        "emergency_contact": "+0987654321"
    }
    
    response = client.post(
        "/api/v1/drivers",
        json=driver_data,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["license_number"] == "DL-123456"
    assert data["user"]["email"] == "driver1@transitops.com"
    assert data["status"] == "Available"
    assert data["safety_score"] == "100.00"


def test_create_driver_duplicate_license(
    client: TestClient,
    db_session: Session,
    driver_role: Role,
    fleet_manager_token: str
):
    """Test creating driver with duplicate license number."""
    # Create first driver
    user1 = User(
        email="driver1@transitops.com",
        password_hash=get_password_hash("password"),
        first_name="Driver",
        last_name="One",
        role_id=driver_role.id,
        is_active=True
    )
    db_session.add(user1)
    db_session.commit()
    
    driver1 = Driver(
        user_id=user1.id,
        license_number="DL-123456",
        license_category="HMV",
        license_issue_date=date(2020, 1, 1),
        license_expiry_date=date(2030, 12, 31),
        date_of_birth=date(1990, 5, 15)
    )
    db_session.add(driver1)
    db_session.commit()
    
    # Try to create second driver with same license
    driver_data = {
        "user": {
            "email": "driver2@transitops.com",
            "password": "driver123",
            "first_name": "Driver",
            "last_name": "Two"
        },
        "license_number": "DL-123456",
        "license_category": "LMV",
        "license_issue_date": "2021-01-01",
        "license_expiry_date": "2031-12-31",
        "date_of_birth": "1992-06-20"
    }
    
    response = client.post(
        "/api/v1/drivers",
        json=driver_data,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["error"]["message"].lower()


def test_create_driver_expired_license(
    client: TestClient,
    db_session: Session,
    driver_role: Role,
    fleet_manager_token: str
):
    """Test creating driver with expired license."""
    driver_data = {
        "user": {
            "email": "driver3@transitops.com",
            "password": "driver123",
            "first_name": "Expired",
            "last_name": "License"
        },
        "license_number": "DL-999999",
        "license_category": "LMV",
        "license_issue_date": "2015-01-01",
        "license_expiry_date": "2020-12-31",  # Expired
        "date_of_birth": "1990-01-01"
    }
    
    response = client.post(
        "/api/v1/drivers",
        json=driver_data,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 422  # Validation error


def test_create_driver_underage(
    client: TestClient,
    db_session: Session,
    driver_role: Role,
    fleet_manager_token: str
):
    """Test creating driver under 18 years old."""
    # Calculate date for someone 17 years old
    underage_dob = date.today() - timedelta(days=365 * 17)
    
    driver_data = {
        "user": {
            "email": "young@transitops.com",
            "password": "driver123",
            "first_name": "Too",
            "last_name": "Young"
        },
        "license_number": "DL-YOUNG",
        "license_category": "LMV",
        "license_issue_date": "2024-01-01",
        "license_expiry_date": "2034-12-31",
        "date_of_birth": underage_dob.isoformat()
    }
    
    response = client.post(
        "/api/v1/drivers",
        json=driver_data,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 422  # Validation error


def test_list_drivers(
    client: TestClient,
    db_session: Session,
    driver_role: Role,
    fleet_manager_token: str
):
    """Test listing drivers."""
    # Create test driver
    user = User(
        email="driver@transitops.com",
        password_hash=get_password_hash("password"),
        first_name="Test",
        last_name="Driver",
        role_id=driver_role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    driver = Driver(
        user_id=user.id,
        license_number="DL-TEST",
        license_category="HMV",
        license_issue_date=date(2020, 1, 1),
        license_expiry_date=date(2030, 12, 31),
        date_of_birth=date(1990, 5, 15)
    )
    db_session.add(driver)
    db_session.commit()
    
    response = client.get(
        "/api/v1/drivers",
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0
    assert "pagination" in data


def test_get_driver_by_id(
    client: TestClient,
    db_session: Session,
    driver_role: Role,
    fleet_manager_token: str
):
    """Test getting driver by ID."""
    # Create test driver
    user = User(
        email="specific@transitops.com",
        password_hash=get_password_hash("password"),
        first_name="Specific",
        last_name="Driver",
        role_id=driver_role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    driver = Driver(
        user_id=user.id,
        license_number="DL-SPECIFIC",
        license_category="LMV",
        license_issue_date=date(2021, 1, 1),
        license_expiry_date=date(2031, 12, 31),
        date_of_birth=date(1985, 3, 20)
    )
    db_session.add(driver)
    db_session.commit()
    
    response = client.get(
        f"/api/v1/drivers/{driver.id}",
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["license_number"] == "DL-SPECIFIC"
    assert data["user"]["email"] == "specific@transitops.com"


def test_update_driver(
    client: TestClient,
    db_session: Session,
    driver_role: Role,
    fleet_manager_token: str
):
    """Test updating driver."""
    # Create test driver
    user = User(
        email="updateme@transitops.com",
        password_hash=get_password_hash("password"),
        first_name="Update",
        last_name="Me",
        role_id=driver_role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    driver = Driver(
        user_id=user.id,
        license_number="DL-UPDATE",
        license_category="LMV",
        license_issue_date=date(2020, 1, 1),
        license_expiry_date=date(2030, 12, 31),
        date_of_birth=date(1988, 7, 10)
    )
    db_session.add(driver)
    db_session.commit()
    
    # Update driver
    update_data = {
        "emergency_contact": "+1111111111",
        "safety_score": 95.5
    }
    
    response = client.put(
        f"/api/v1/drivers/{driver.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["emergency_contact"] == "+1111111111"
    assert float(data["safety_score"]) == 95.5


def test_delete_driver(
    client: TestClient,
    db_session: Session,
    driver_role: Role,
    fleet_manager_token: str
):
    """Test deleting driver."""
    # Create test driver
    user = User(
        email="deleteme@transitops.com",
        password_hash=get_password_hash("password"),
        first_name="Delete",
        last_name="Me",
        role_id=driver_role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    driver = Driver(
        user_id=user.id,
        license_number="DL-DELETE",
        license_category="LMV",
        license_issue_date=date(2020, 1, 1),
        license_expiry_date=date(2030, 12, 31),
        date_of_birth=date(1992, 4, 25),
        status="Available"
    )
    db_session.add(driver)
    db_session.commit()
    driver_id = driver.id
    
    response = client.delete(
        f"/api/v1/drivers/{driver_id}",
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # Verify driver is deleted
    deleted_driver = db_session.query(Driver).filter(Driver.id == driver_id).first()
    assert deleted_driver is None


def test_get_available_drivers(
    client: TestClient,
    db_session: Session,
    driver_role: Role,
    fleet_manager_token: str
):
    """Test getting available drivers."""
    # Create available driver
    user = User(
        email="available@transitops.com",
        password_hash=get_password_hash("password"),
        first_name="Available",
        last_name="Driver",
        role_id=driver_role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    driver = Driver(
        user_id=user.id,
        license_number="DL-AVAIL",
        license_category="HMV",
        license_issue_date=date(2020, 1, 1),
        license_expiry_date=date(2030, 12, 31),
        date_of_birth=date(1987, 9, 12),
        status="Available"
    )
    db_session.add(driver)
    db_session.commit()
    
    response = client.get(
        "/api/v1/drivers/available/list",
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(d["status"] == "Available" for d in data)
