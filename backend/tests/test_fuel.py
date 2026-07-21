"""
Test fuel endpoints.
"""
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
from uuid import uuid4

from app.models.role import Role
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.fuel import Fuel
from app.core.security import get_password_hash


@pytest.fixture
def fuel_manager_user(db_session: Session) -> User:
    """Create Fuel Manager user for testing."""
    role = Role(
        name="Fuel Manager",
        permissions={
            "vehicles": ["read"],
            "fuel": ["read", "create", "update", "delete"]
        }
    )
    db_session.add(role)
    db_session.commit()

    user = User(
        email="fuel@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="Fuel",
        last_name="Manager",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def fuel_manager_token(client: TestClient, fuel_manager_user: User) -> str:
    """Get JWT token for Fuel Manager."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "fuel@transitops.com",
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
        capacity_kg=Decimal("15000.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("45000.00"),
        status="Available"
    )
    db_session.add(vehicle)
    db_session.commit()
    db_session.refresh(vehicle)
    return vehicle


def _fuel_payload(vehicle_id):
    """Helper to build a fuel creation payload."""
    return {
        "vehicle_id": str(vehicle_id),
        "fuel_type": "Diesel",
        "quantity_liters": 50.00,
        "cost_per_liter": 90.00,
        "odometer_reading": 45100.00,
        "refuel_date": datetime.now(timezone.utc).isoformat(),
        "station_name": "Indian Oil",
        "location": "Delhi"
    }


# ============================================================
# CREATE FUEL TESTS
# ============================================================

def test_create_fuel_success(
    client: TestClient,
    db_session: Session,
    fuel_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test successful fuel creation."""
    payload = _fuel_payload(sample_vehicle.id)

    response = client.post(
        "/api/v1/fuel",
        json=payload,
        headers={"Authorization": f"Bearer {fuel_manager_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["fuel_type"] == "Diesel"
    assert float(data["total_cost"]) == 4500.00  # Auto-calculated 50 * 90
    assert data["vehicle"]["registration_number"] == "DL-01-AB-1234"


def test_create_fuel_vehicle_not_found(
    client: TestClient,
    db_session: Session,
    fuel_manager_token: str
):
    """Test creating fuel with non-existent vehicle."""
    payload = _fuel_payload(uuid4())

    response = client.post(
        "/api/v1/fuel",
        json=payload,
        headers={"Authorization": f"Bearer {fuel_manager_token}"}
    )

    assert response.status_code == 400
    assert "not found" in response.json()["error"]["message"].lower()


def test_create_fuel_type_mismatch(
    client: TestClient,
    db_session: Session,
    fuel_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test creating fuel with mismatched type."""
    payload = _fuel_payload(sample_vehicle.id)
    payload["fuel_type"] = "Petrol"

    response = client.post(
        "/api/v1/fuel",
        json=payload,
        headers={"Authorization": f"Bearer {fuel_manager_token}"}
    )

    assert response.status_code == 400
    assert "mismatch" in response.json()["error"]["message"].lower()


def test_create_fuel_invalid_quantity(
    client: TestClient,
    db_session: Session,
    fuel_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test creating fuel with zero/negative quantity."""
    payload = _fuel_payload(sample_vehicle.id)
    payload["quantity_liters"] = -5.0

    response = client.post(
        "/api/v1/fuel",
        json=payload,
        headers={"Authorization": f"Bearer {fuel_manager_token}"}
    )

    assert response.status_code == 422


def test_create_fuel_future_date(
    client: TestClient,
    db_session: Session,
    fuel_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test creating fuel with a future date."""
    payload = _fuel_payload(sample_vehicle.id)
    future = datetime.now(timezone.utc) + timedelta(days=1)
    payload["refuel_date"] = future.isoformat()

    response = client.post(
        "/api/v1/fuel",
        json=payload,
        headers={"Authorization": f"Bearer {fuel_manager_token}"}
    )

    assert response.status_code == 400
    assert "future" in response.json()["error"]["message"].lower()


def test_create_fuel_invalid_odometer(
    client: TestClient,
    db_session: Session,
    fuel_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test creating fuel with odometer less than vehicle's current."""
    payload = _fuel_payload(sample_vehicle.id)
    payload["odometer_reading"] = 1000.00  # Current is 45000

    response = client.post(
        "/api/v1/fuel",
        json=payload,
        headers={"Authorization": f"Bearer {fuel_manager_token}"}
    )

    assert response.status_code == 400
    assert "cannot be less than vehicle's current" in response.json()["error"]["message"].lower()


# ============================================================
# LIST / GET TESTS
# ============================================================

def test_list_fuel(
    client: TestClient,
    db_session: Session,
    fuel_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test listing fuel with pagination."""
    payload = _fuel_payload(sample_vehicle.id)
    client.post(
        "/api/v1/fuel",
        json=payload,
        headers={"Authorization": f"Bearer {fuel_manager_token}"}
    )

    response = client.get(
        "/api/v1/fuel",
        headers={"Authorization": f"Bearer {fuel_manager_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0
    assert "pagination" in data


def test_get_fuel_by_id(
    client: TestClient,
    db_session: Session,
    fuel_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test getting fuel by ID."""
    payload = _fuel_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/fuel",
        json=payload,
        headers={"Authorization": f"Bearer {fuel_manager_token}"}
    )
    record_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/fuel/{record_id}",
        headers={"Authorization": f"Bearer {fuel_manager_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == record_id
    assert float(data["total_cost"]) == 4500.00


# ============================================================
# UPDATE TESTS
# ============================================================

def test_update_fuel(
    client: TestClient,
    db_session: Session,
    fuel_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test updating a fuel record recalculates cost."""
    payload = _fuel_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/fuel",
        json=payload,
        headers={"Authorization": f"Bearer {fuel_manager_token}"}
    )
    record_id = create_response.json()["id"]

    update_data = {
        "quantity_liters": 60.00,
        "cost_per_liter": 95.00
    }

    response = client.put(
        f"/api/v1/fuel/{record_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {fuel_manager_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert float(data["quantity_liters"]) == 60.00
    assert float(data["total_cost"]) == 5700.00  # 60 * 95


# ============================================================
# DELETE TESTS
# ============================================================

def test_delete_fuel(
    client: TestClient,
    db_session: Session,
    fuel_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test deleting a fuel record."""
    payload = _fuel_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/fuel",
        json=payload,
        headers={"Authorization": f"Bearer {fuel_manager_token}"}
    )
    record_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/fuel/{record_id}",
        headers={"Authorization": f"Bearer {fuel_manager_token}"}
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    # Verify record is deleted
    deleted = db_session.query(Fuel).filter(
        Fuel.id == record_id
    ).first()
    assert deleted is None


# ============================================================
# STATS TESTS
# ============================================================

def test_get_fuel_efficiency(
    client: TestClient,
    db_session: Session,
    fuel_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test getting fuel efficiency stats."""
    payload = _fuel_payload(sample_vehicle.id)
    # Refuel 1: 50 liters, odometer 45100 (start 45000 -> dist 100)
    client.post("/api/v1/fuel", json=payload, headers={"Authorization": f"Bearer {fuel_manager_token}"})
    
    # Refuel 2: 50 liters, odometer 45500
    payload2 = payload.copy()
    payload2["odometer_reading"] = 45500.00
    client.post("/api/v1/fuel", json=payload2, headers={"Authorization": f"Bearer {fuel_manager_token}"})

    response = client.get(
        "/api/v1/fuel/efficiency",
        headers={"Authorization": f"Bearer {fuel_manager_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Simplified efficiency formula from query should yield:
    # total_dist = 45500 - 45100 = 400
    # total_fuel = 100 liters
    # avg = 4.0 kmpl
    stats = data["data"][0]
    assert stats["vehicle_id"] == str(sample_vehicle.id)
    assert float(stats["total_fuel_consumed"]) == 100.00
    assert float(stats["total_distance"]) == 400.00
    assert float(stats["avg_fuel_efficiency_kmpl"]) == 4.0
