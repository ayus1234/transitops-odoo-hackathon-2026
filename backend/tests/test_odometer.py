"""
Tests for Odometer History feature.
"""
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.role import Role
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.odometer_reading import OdometerReading
from app.core.security import get_password_hash


@pytest.fixture
def odo_user(db_session: Session) -> User:
    """Create user for odometer testing."""
    role = Role(
        name="Fleet Manager ODO",
        permissions={"vehicles": ["read", "create", "update", "delete"]}
    )
    db_session.add(role)
    db_session.commit()

    user = User(
        email="odo_manager@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="Odo",
        last_name="Manager",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def odo_token(client: TestClient, odo_user: User) -> str:
    """Get JWT token for odometer tester."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "odo_manager@transitops.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def odo_vehicle(db_session: Session) -> Vehicle:
    """Create a test vehicle for odometer tests."""
    vehicle = Vehicle(
        registration_number="ODO-TEST-001",
        vehicle_name="Odometer Test Truck",
        vehicle_type="Truck",
        capacity_kg=Decimal("10000.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("50000.00"),
        status="Available"
    )
    db_session.add(vehicle)
    db_session.commit()
    db_session.refresh(vehicle)
    return vehicle


# ── Record Readings ──

def test_record_odometer_reading(
    client: TestClient,
    odo_token: str,
    odo_vehicle: Vehicle
):
    """Test recording a new odometer reading."""
    response = client.post(
        f"/api/v1/vehicles/{odo_vehicle.id}/odometer",
        json={
            "reading_km": 51000.00,
            "source": "manual",
            "notes": "Monthly check"
        },
        headers={"Authorization": f"Bearer {odo_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert float(data["reading_km"]) == 51000.00
    assert data["source"] == "manual"
    assert data["vehicle_id"] == str(odo_vehicle.id)


def test_record_odometer_syncs_vehicle(
    client: TestClient,
    odo_token: str,
    odo_vehicle: Vehicle
):
    """Test that recording a reading updates Vehicle.current_odometer_km."""
    # Record a new reading
    client.post(
        f"/api/v1/vehicles/{odo_vehicle.id}/odometer",
        json={"reading_km": 52000.00, "source": "manual"},
        headers={"Authorization": f"Bearer {odo_token}"}
    )

    # Check vehicle was updated
    response = client.get(
        f"/api/v1/vehicles/{odo_vehicle.id}",
        headers={"Authorization": f"Bearer {odo_token}"}
    )

    assert response.status_code == 200
    assert float(response.json()["current_odometer_km"]) == 52000.00


def test_anti_regression_blocks_lower_reading(
    client: TestClient,
    db_session: Session,
    odo_token: str,
    odo_vehicle: Vehicle
):
    """Test that a reading lower than the previous is rejected."""
    # Insert an initial reading
    reading = OdometerReading(
        vehicle_id=odo_vehicle.id,
        reading_km=Decimal("55000.00"),
        recorded_at=datetime.now(timezone.utc),
        source="manual"
    )
    db_session.add(reading)
    db_session.commit()

    # Try to record a lower reading
    response = client.post(
        f"/api/v1/vehicles/{odo_vehicle.id}/odometer",
        json={"reading_km": 54000.00, "source": "manual"},
        headers={"Authorization": f"Bearer {odo_token}"}
    )

    assert response.status_code == 400
    assert "less than" in response.json()["error"]["message"].lower()


def test_correction_overrides_anti_regression(
    client: TestClient,
    db_session: Session,
    odo_token: str,
    odo_vehicle: Vehicle
):
    """Test that source='correction' allows a lower reading."""
    # Insert an initial reading
    reading = OdometerReading(
        vehicle_id=odo_vehicle.id,
        reading_km=Decimal("60000.00"),
        recorded_at=datetime.now(timezone.utc),
        source="manual"
    )
    db_session.add(reading)
    db_session.commit()

    # Record a correction (lower value)
    response = client.post(
        f"/api/v1/vehicles/{odo_vehicle.id}/odometer",
        json={
            "reading_km": 58000.00,
            "source": "correction",
            "notes": "Gauge was mis-calibrated"
        },
        headers={"Authorization": f"Bearer {odo_token}"}
    )

    assert response.status_code == 201
    assert float(response.json()["reading_km"]) == 58000.00


def test_record_multiple_readings_ascending(
    client: TestClient,
    odo_token: str,
    odo_vehicle: Vehicle
):
    """Test recording multiple ascending readings in sequence."""
    readings = [51000, 52500, 54000, 55500]
    for km in readings:
        response = client.post(
            f"/api/v1/vehicles/{odo_vehicle.id}/odometer",
            json={"reading_km": km, "source": "manual"},
            headers={"Authorization": f"Bearer {odo_token}"}
        )
        assert response.status_code == 201


# ── History ──

def test_get_odometer_history(
    client: TestClient,
    db_session: Session,
    odo_token: str,
    odo_vehicle: Vehicle
):
    """Test retrieving paginated odometer history."""
    # Insert a few readings
    for i in range(3):
        r = OdometerReading(
            vehicle_id=odo_vehicle.id,
            reading_km=Decimal(str(50000 + (i + 1) * 1000)),
            recorded_at=datetime.now(timezone.utc),
            source="manual"
        )
        db_session.add(r)
    db_session.commit()

    response = client.get(
        f"/api/v1/vehicles/{odo_vehicle.id}/odometer",
        headers={"Authorization": f"Bearer {odo_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 3
    assert "pagination" in data


# ── Stats ──

def test_get_odometer_stats(
    client: TestClient,
    db_session: Session,
    odo_token: str,
    odo_vehicle: Vehicle
):
    """Test retrieving odometer statistics."""
    # Insert readings
    for i, km in enumerate([50000, 52000, 55000]):
        r = OdometerReading(
            vehicle_id=odo_vehicle.id,
            reading_km=Decimal(str(km)),
            recorded_at=datetime.now(timezone.utc),
            source="manual"
        )
        db_session.add(r)
    db_session.commit()

    response = client.get(
        f"/api/v1/vehicles/{odo_vehicle.id}/odometer/stats",
        headers={"Authorization": f"Bearer {odo_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_readings"] == 3
    assert float(data["total_distance_km"]) == 5000.00


def test_odometer_for_nonexistent_vehicle(
    client: TestClient,
    odo_token: str
):
    """Test odometer endpoints for non-existent vehicle."""
    import uuid
    fake_id = uuid.uuid4()

    response = client.get(
        f"/api/v1/vehicles/{fake_id}/odometer",
        headers={"Authorization": f"Bearer {odo_token}"}
    )
    assert response.status_code == 400

    response2 = client.post(
        f"/api/v1/vehicles/{fake_id}/odometer",
        json={"reading_km": 1000, "source": "manual"},
        headers={"Authorization": f"Bearer {odo_token}"}
    )
    assert response2.status_code == 400
