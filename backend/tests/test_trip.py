"""
Test trip endpoints.
"""
import pytest
from datetime import date, datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.role import Role
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.trip import Trip
from app.core.security import get_password_hash


@pytest.fixture
def fleet_manager_user(db_session: Session) -> User:
    """Create Fleet Manager user for testing."""
    role = Role(
        name="Fleet Manager",
        permissions={
            "vehicles": ["read", "create", "update", "delete"],
            "drivers": ["read", "create", "update", "delete"],
            "trips": ["read", "create", "update", "delete"]
        }
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


@pytest.fixture
def sample_vehicle(db_session: Session) -> Vehicle:
    """Create a sample vehicle for testing."""
    vehicle = Vehicle(
        registration_number="DL-01-AB-1234",
        vehicle_name="Tata LPT 1618",
        vehicle_type="Truck",
        manufacturer="Tata Motors",
        model="LPT 1618",
        year=2022,
        capacity_kg=Decimal("5000.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("45000.00"),
        status="Available"
    )
    db_session.add(vehicle)
    db_session.commit()
    db_session.refresh(vehicle)
    return vehicle


@pytest.fixture
def sample_driver(db_session: Session, fleet_manager_user: User) -> Driver:
    """Create a sample driver for testing."""
    # Create driver user account
    role = db_session.query(Role).filter(Role.name == "Fleet Manager").first()
    
    driver_user = User(
        email="driver@transitops.com",
        password_hash=get_password_hash("driverpass"),
        first_name="Rajesh",
        last_name="Kumar",
        role_id=role.id,
        is_active=True
    )
    db_session.add(driver_user)
    db_session.commit()
    
    driver = Driver(
        user_id=driver_user.id,
        license_number="DL-1234567890",
        license_category="HMV",
        license_issue_date=date(2020, 1, 1),
        license_expiry_date=date(2028, 12, 31),
        date_of_birth=date(1985, 5, 15),
        emergency_contact="+919876543211",
        safety_score=Decimal("95.50"),
        total_trips=100,
        status="Available"
    )
    db_session.add(driver)
    db_session.commit()
    db_session.refresh(driver)
    return driver


def _trip_payload(vehicle_id, driver_id):
    """Helper to build a trip creation payload."""
    departure = datetime.utcnow() + timedelta(hours=1)
    arrival = departure + timedelta(hours=6)
    return {
        "vehicle_id": str(vehicle_id),
        "driver_id": str(driver_id),
        "source": "Delhi",
        "destination": "Jaipur",
        "cargo_weight_kg": 4500.00,
        "planned_distance_km": 280.00,
        "planned_departure": departure.isoformat(),
        "planned_arrival": arrival.isoformat(),
        "notes": "Handle with care"
    }


# ============================================================
# CREATE TRIP TESTS
# ============================================================

def test_create_trip_success(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle,
    sample_driver: Driver
):
    """Test successful trip creation."""
    payload = _trip_payload(sample_vehicle.id, sample_driver.id)
    
    response = client.post(
        "/api/v1/trips",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "Draft"
    assert data["source"] == "Delhi"
    assert data["destination"] == "Jaipur"
    assert data["trip_number"].startswith("TRP-")
    assert data["vehicle"]["registration_number"] == "DL-01-AB-1234"


def test_create_trip_vehicle_not_found(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_driver: Driver
):
    """Test creating trip with non-existent vehicle."""
    from uuid import uuid4
    payload = _trip_payload(uuid4(), sample_driver.id)
    
    response = client.post(
        "/api/v1/trips",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 400
    assert "not found" in response.json()["error"]["message"].lower()


def test_create_trip_driver_not_found(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test creating trip with non-existent driver."""
    from uuid import uuid4
    payload = _trip_payload(sample_vehicle.id, uuid4())
    
    response = client.post(
        "/api/v1/trips",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 400
    assert "not found" in response.json()["error"]["message"].lower()


def test_create_trip_vehicle_unavailable(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle,
    sample_driver: Driver
):
    """Test creating trip with unavailable vehicle."""
    sample_vehicle.status = "In Shop"
    db_session.commit()
    
    payload = _trip_payload(sample_vehicle.id, sample_driver.id)
    
    response = client.post(
        "/api/v1/trips",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 400
    assert "not available" in response.json()["error"]["message"].lower()


def test_create_trip_driver_unavailable(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle,
    sample_driver: Driver
):
    """Test creating trip with unavailable driver."""
    sample_driver.status = "Off Duty"
    db_session.commit()
    
    payload = _trip_payload(sample_vehicle.id, sample_driver.id)
    
    response = client.post(
        "/api/v1/trips",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 400
    assert "not available" in response.json()["error"]["message"].lower()


def test_create_trip_cargo_exceeds_capacity(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle,
    sample_driver: Driver
):
    """Test creating trip with cargo exceeding vehicle capacity."""
    payload = _trip_payload(sample_vehicle.id, sample_driver.id)
    payload["cargo_weight_kg"] = 9999.00  # Vehicle capacity is 5000 kg
    
    response = client.post(
        "/api/v1/trips",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 400
    assert "exceeds" in response.json()["error"]["message"].lower()


def test_create_trip_invalid_times(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle,
    sample_driver: Driver
):
    """Test creating trip with arrival before departure."""
    departure = datetime.utcnow() + timedelta(hours=6)
    arrival = datetime.utcnow() + timedelta(hours=1)  # Before departure
    
    payload = _trip_payload(sample_vehicle.id, sample_driver.id)
    payload["planned_departure"] = departure.isoformat()
    payload["planned_arrival"] = arrival.isoformat()
    
    response = client.post(
        "/api/v1/trips",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 422  # Pydantic validation error


# ============================================================
# LIST / GET TRIP TESTS
# ============================================================

def test_list_trips(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle,
    sample_driver: Driver
):
    """Test listing trips with pagination."""
    # Create a trip via API
    payload = _trip_payload(sample_vehicle.id, sample_driver.id)
    client.post(
        "/api/v1/trips",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    response = client.get(
        "/api/v1/trips",
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0
    assert "pagination" in data


def test_get_trip_by_id(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle,
    sample_driver: Driver
):
    """Test getting trip by ID."""
    # Create a trip
    payload = _trip_payload(sample_vehicle.id, sample_driver.id)
    create_response = client.post(
        "/api/v1/trips",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    trip_id = create_response.json()["id"]
    
    response = client.get(
        f"/api/v1/trips/{trip_id}",
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == trip_id
    assert data["source"] == "Delhi"
    assert data["destination"] == "Jaipur"


# ============================================================
# UPDATE TRIP TESTS
# ============================================================

def test_update_draft_trip(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle,
    sample_driver: Driver
):
    """Test updating a draft trip."""
    # Create a trip
    payload = _trip_payload(sample_vehicle.id, sample_driver.id)
    create_response = client.post(
        "/api/v1/trips",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    trip_id = create_response.json()["id"]
    
    # Update trip
    update_data = {
        "source": "Mumbai",
        "destination": "Pune",
        "planned_distance_km": 150.00
    }
    
    response = client.put(
        f"/api/v1/trips/{trip_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "Mumbai"
    assert data["destination"] == "Pune"


# ============================================================
# DELETE TRIP TESTS
# ============================================================

def test_delete_draft_trip(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle,
    sample_driver: Driver
):
    """Test deleting a draft trip."""
    # Create a trip
    payload = _trip_payload(sample_vehicle.id, sample_driver.id)
    create_response = client.post(
        "/api/v1/trips",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    trip_id = create_response.json()["id"]
    
    response = client.delete(
        f"/api/v1/trips/{trip_id}",
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    
    # Verify trip is deleted
    deleted_trip = db_session.query(Trip).filter(Trip.id == trip_id).first()
    assert deleted_trip is None


# ============================================================
# DISPATCH TRIP TESTS
# ============================================================

def test_dispatch_trip_success(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle,
    sample_driver: Driver
):
    """Test dispatching a trip successfully."""
    # Create a trip
    payload = _trip_payload(sample_vehicle.id, sample_driver.id)
    create_response = client.post(
        "/api/v1/trips",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    trip_id = create_response.json()["id"]
    
    # Dispatch
    response = client.post(
        f"/api/v1/trips/{trip_id}/dispatch",
        json={"start_odometer_km": 45000.00},
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Dispatched"
    assert data["start_odometer_km"] is not None
    
    # Verify vehicle status changed
    db_session.refresh(sample_vehicle)
    assert sample_vehicle.status == "On Trip"
    
    # Verify driver status changed
    db_session.refresh(sample_driver)
    assert sample_driver.status == "On Trip"


# ============================================================
# COMPLETE TRIP TESTS
# ============================================================

def test_complete_trip_success(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle,
    sample_driver: Driver
):
    """Test completing a trip successfully."""
    initial_total_trips = sample_driver.total_trips
    
    # Create and dispatch trip
    payload = _trip_payload(sample_vehicle.id, sample_driver.id)
    create_response = client.post(
        "/api/v1/trips",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    trip_id = create_response.json()["id"]
    
    client.post(
        f"/api/v1/trips/{trip_id}/dispatch",
        json={"start_odometer_km": 45000.00},
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    # Complete
    response = client.post(
        f"/api/v1/trips/{trip_id}/complete",
        json={
            "end_odometer_km": 45280.00,
            "actual_distance_km": 280.00,
            "fuel_consumed_liters": 35.00,
            "notes": "Delivery completed successfully"
        },
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Completed"
    
    # Verify vehicle status restored
    db_session.refresh(sample_vehicle)
    assert sample_vehicle.status == "Available"
    assert float(sample_vehicle.current_odometer_km) == 45280.00
    
    # Verify driver status restored and total_trips incremented
    db_session.refresh(sample_driver)
    assert sample_driver.status == "Available"
    assert sample_driver.total_trips == initial_total_trips + 1


# ============================================================
# CANCEL TRIP TESTS
# ============================================================

def test_cancel_draft_trip(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle,
    sample_driver: Driver
):
    """Test cancelling a draft trip."""
    # Create a trip
    payload = _trip_payload(sample_vehicle.id, sample_driver.id)
    create_response = client.post(
        "/api/v1/trips",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    trip_id = create_response.json()["id"]
    
    # Cancel
    response = client.post(
        f"/api/v1/trips/{trip_id}/cancel",
        json={"reason": "Customer request"},
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Cancelled"


def test_cancel_dispatched_trip_restores_status(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle,
    sample_driver: Driver
):
    """Test cancelling a dispatched trip restores vehicle and driver status."""
    # Create and dispatch trip
    payload = _trip_payload(sample_vehicle.id, sample_driver.id)
    create_response = client.post(
        "/api/v1/trips",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    trip_id = create_response.json()["id"]
    
    client.post(
        f"/api/v1/trips/{trip_id}/dispatch",
        json={"start_odometer_km": 45000.00},
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    # Verify vehicle and driver are On Trip
    db_session.refresh(sample_vehicle)
    db_session.refresh(sample_driver)
    assert sample_vehicle.status == "On Trip"
    assert sample_driver.status == "On Trip"
    
    # Cancel
    response = client.post(
        f"/api/v1/trips/{trip_id}/cancel",
        json={"reason": "Route blocked due to weather"},
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "Cancelled"
    
    # Verify vehicle and driver restored
    db_session.refresh(sample_vehicle)
    db_session.refresh(sample_driver)
    assert sample_vehicle.status == "Available"
    assert sample_driver.status == "Available"
