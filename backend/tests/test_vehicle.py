"""
Test vehicle endpoints.
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.role import Role
from app.models.user import User
from app.models.vehicle import Vehicle
from app.core.security import get_password_hash


@pytest.fixture
def fleet_manager_user(db_session: Session) -> User:
    """Create Fleet Manager user for testing."""
    role = Role(
        name="Fleet Manager",
        permissions={"vehicles": ["read", "create", "update", "delete"]}
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


def test_create_vehicle_success(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str
):
    """Test successful vehicle creation."""
    # Prepare vehicle data
    vehicle_data = {
        "registration_number": "TN-01-AB-1234",
        "vehicle_name": "Tata LPT 1518",
        "vehicle_type": "Truck",
        "manufacturer": "Tata Motors",
        "model": "LPT 1518",
        "year": 2022,
        "capacity_kg": 15000.00,
        "fuel_type": "Diesel",
        "current_odometer_km": 5000.00,
        "acquisition_cost": 2500000.00,
        "acquisition_date": "2022-06-15",
        "insurance_expiry": "2026-06-30"
    }
    
    response = client.post(
        "/api/v1/vehicles",
        json=vehicle_data,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["registration_number"] == "TN-01-AB-1234"
    assert data["vehicle_name"] == "Tata LPT 1518"
    assert data["status"] == "Available"


def test_create_vehicle_duplicate_registration(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str
):
    """Test creating vehicle with duplicate registration number."""
    # Create first vehicle
    vehicle1 = Vehicle(
        registration_number="TN-02-CD-5678",
        vehicle_name="Ashok Leyland",
        vehicle_type="Truck",
        capacity_kg=Decimal("12000.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("3000.00")
    )
    db_session.add(vehicle1)
    db_session.commit()
    
    # Try to create second vehicle with same registration
    vehicle_data = {
        "registration_number": "TN-02-CD-5678",
        "vehicle_name": "Another Truck",
        "vehicle_type": "Truck",
        "capacity_kg": 10000.00,
        "fuel_type": "Diesel"
    }
    
    response = client.post(
        "/api/v1/vehicles",
        json=vehicle_data,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["error"]["message"].lower()


def test_create_vehicle_invalid_type(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str
):
    """Test creating vehicle with invalid vehicle type."""
    vehicle_data = {
        "registration_number": "TN-03-EF-9999",
        "vehicle_name": "Test Vehicle",
        "vehicle_type": "Spaceship",  # Invalid type
        "capacity_kg": 5000.00,
        "fuel_type": "Diesel"
    }
    
    response = client.post(
        "/api/v1/vehicles",
        json=vehicle_data,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 422  # Validation error


def test_create_vehicle_invalid_fuel_type(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str
):
    """Test creating vehicle with invalid fuel type."""
    vehicle_data = {
        "registration_number": "TN-04-GH-1111",
        "vehicle_name": "Test Vehicle",
        "vehicle_type": "Truck",
        "capacity_kg": 8000.00,
        "fuel_type": "Nuclear"  # Invalid fuel type
    }
    
    response = client.post(
        "/api/v1/vehicles",
        json=vehicle_data,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 422  # Validation error


def test_list_vehicles(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str
):
    """Test listing vehicles."""
    # Create test vehicle
    vehicle = Vehicle(
        registration_number="TN-05-IJ-2222",
        vehicle_name="Test Truck",
        vehicle_type="Truck",
        capacity_kg=Decimal("10000.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("2000.00")
    )
    db_session.add(vehicle)
    db_session.commit()
    
    response = client.get(
        "/api/v1/vehicles",
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0
    assert "pagination" in data


def test_get_vehicle_by_id(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str
):
    """Test getting vehicle by ID."""
    # Create test vehicle
    vehicle = Vehicle(
        registration_number="TN-06-KL-3333",
        vehicle_name="Specific Vehicle",
        vehicle_type="Van",
        manufacturer="Mahindra",
        model="Supro",
        capacity_kg=Decimal("1500.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("15000.00")
    )
    db_session.add(vehicle)
    db_session.commit()
    
    response = client.get(
        f"/api/v1/vehicles/{vehicle.id}",
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["registration_number"] == "TN-06-KL-3333"
    assert data["vehicle_name"] == "Specific Vehicle"


def test_update_vehicle(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str
):
    """Test updating vehicle."""
    # Create test vehicle
    vehicle = Vehicle(
        registration_number="TN-07-MN-4444",
        vehicle_name="Update Me",
        vehicle_type="Truck",
        capacity_kg=Decimal("12000.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("5000.00")
    )
    db_session.add(vehicle)
    db_session.commit()
    
    # Update vehicle
    update_data = {
        "current_odometer_km": 6500.00,
        "status": "In Shop"
    }
    
    response = client.put(
        f"/api/v1/vehicles/{vehicle.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert float(data["current_odometer_km"]) == 6500.00
    assert data["status"] == "In Shop"


def test_delete_vehicle(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str
):
    """Test deleting vehicle."""
    # Create test vehicle
    vehicle = Vehicle(
        registration_number="TN-08-OP-5555",
        vehicle_name="Delete Me",
        vehicle_type="Pickup",
        capacity_kg=Decimal("2000.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("8000.00"),
        status="Available"
    )
    db_session.add(vehicle)
    db_session.commit()
    vehicle_id = vehicle.id
    
    response = client.delete(
        f"/api/v1/vehicles/{vehicle_id}",
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # Verify vehicle is deleted
    deleted_vehicle = db_session.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    assert deleted_vehicle is None


def test_search_vehicles(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str
):
    """Test searching vehicles."""
    # Create test vehicles
    vehicle1 = Vehicle(
        registration_number="TN-09-QR-6666",
        vehicle_name="Tata Ace",
        vehicle_type="Pickup",
        capacity_kg=Decimal("1500.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("10000.00")
    )
    vehicle2 = Vehicle(
        registration_number="TN-10-ST-7777",
        vehicle_name="Mahindra Bolero",
        vehicle_type="Pickup",
        capacity_kg=Decimal("1800.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("5000.00")
    )
    db_session.add_all([vehicle1, vehicle2])
    db_session.commit()
    
    response = client.get(
        "/api/v1/vehicles/search?query=Pickup",
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
