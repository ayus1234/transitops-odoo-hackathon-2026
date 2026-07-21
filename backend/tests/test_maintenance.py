"""
Test maintenance endpoints.
"""
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.role import Role
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.maintenance import Maintenance
from app.core.security import get_password_hash


@pytest.fixture
def fleet_manager_user(db_session: Session) -> User:
    """Create Fleet Manager user for testing."""
    role = Role(
        name="Fleet Manager",
        permissions={
            "vehicles": ["read", "create", "update", "delete"],
            "drivers": ["read", "create", "update", "delete"],
            "trips": ["read", "create", "update", "delete"],
            "maintenance": ["read", "create", "update", "delete"]
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
        capacity_kg=Decimal("15000.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("45000.00"),
        status="Available"
    )
    db_session.add(vehicle)
    db_session.commit()
    db_session.refresh(vehicle)
    return vehicle


def _maintenance_payload(vehicle_id):
    """Helper to build a maintenance creation payload."""
    return {
        "vehicle_id": str(vehicle_id),
        "maintenance_type": "Oil Change",
        "description": "Regular oil change and filter replacement",
        "priority": "Medium",
        "assigned_technician": "Suresh Sharma",
        "scheduled_date": (date.today() + timedelta(days=7)).isoformat(),
        "estimated_cost": 5000.00,
        "odometer_at_maintenance": 45000.00,
        "notes": "Use synthetic oil"
    }


# ============================================================
# CREATE MAINTENANCE TESTS
# ============================================================

def test_create_maintenance_success(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test successful maintenance creation."""
    payload = _maintenance_payload(sample_vehicle.id)

    response = client.post(
        "/api/v1/maintenance",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "Pending"
    assert data["maintenance_type"] == "Oil Change"
    assert data["maintenance_number"].startswith("MNT-")
    assert data["vehicle"]["registration_number"] == "DL-01-AB-1234"


def test_create_maintenance_vehicle_not_found(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str
):
    """Test creating maintenance with non-existent vehicle."""
    from uuid import uuid4
    payload = _maintenance_payload(uuid4())

    response = client.post(
        "/api/v1/maintenance",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    assert response.status_code == 400
    assert "not found" in response.json()["error"]["message"].lower()


def test_create_maintenance_retired_vehicle(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test creating maintenance for retired vehicle."""
    sample_vehicle.status = "Retired"
    db_session.commit()

    payload = _maintenance_payload(sample_vehicle.id)

    response = client.post(
        "/api/v1/maintenance",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    assert response.status_code == 400
    assert "retired" in response.json()["error"]["message"].lower()


def test_create_maintenance_invalid_type(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test creating maintenance with invalid type."""
    payload = _maintenance_payload(sample_vehicle.id)
    payload["maintenance_type"] = "Rocket Science"

    response = client.post(
        "/api/v1/maintenance",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    assert response.status_code == 422  # Pydantic validation error


def test_create_maintenance_invalid_priority(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test creating maintenance with invalid priority."""
    payload = _maintenance_payload(sample_vehicle.id)
    payload["priority"] = "Ultra"

    response = client.post(
        "/api/v1/maintenance",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    assert response.status_code == 422


def test_create_maintenance_negative_cost(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test creating maintenance with negative estimated cost."""
    payload = _maintenance_payload(sample_vehicle.id)
    payload["estimated_cost"] = -100.00

    response = client.post(
        "/api/v1/maintenance",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    assert response.status_code == 422


# ============================================================
# LIST / GET TESTS
# ============================================================

def test_list_maintenance(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test listing maintenance with pagination."""
    payload = _maintenance_payload(sample_vehicle.id)
    client.post(
        "/api/v1/maintenance",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    response = client.get(
        "/api/v1/maintenance",
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0
    assert "pagination" in data


def test_get_maintenance_by_id(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test getting maintenance by ID."""
    payload = _maintenance_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/maintenance",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    record_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/maintenance/{record_id}",
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == record_id
    assert data["maintenance_type"] == "Oil Change"


# ============================================================
# UPDATE TESTS
# ============================================================

def test_update_pending_maintenance(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test updating a pending maintenance record."""
    payload = _maintenance_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/maintenance",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    record_id = create_response.json()["id"]

    update_data = {
        "priority": "High",
        "estimated_cost": 7500.00,
        "assigned_technician": "Ramesh Kumar"
    }

    response = client.put(
        f"/api/v1/maintenance/{record_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == "High"
    assert float(data["estimated_cost"]) == 7500.00
    assert data["assigned_technician"] == "Ramesh Kumar"


# ============================================================
# DELETE TESTS
# ============================================================

def test_delete_pending_maintenance(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test deleting a pending maintenance record."""
    payload = _maintenance_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/maintenance",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    record_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/maintenance/{record_id}",
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    # Verify record is deleted
    deleted = db_session.query(Maintenance).filter(
        Maintenance.id == record_id
    ).first()
    assert deleted is None


# ============================================================
# STATUS TRANSITION TESTS
# ============================================================

def test_approve_maintenance(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test approving a pending maintenance."""
    payload = _maintenance_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/maintenance",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    record_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/maintenance/{record_id}/status",
        json={"status": "Approved"},
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Approved"


def test_start_maintenance_sets_vehicle_in_shop(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test starting maintenance sets vehicle to In Shop."""
    # Create and approve
    payload = _maintenance_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/maintenance",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    record_id = create_response.json()["id"]

    client.patch(
        f"/api/v1/maintenance/{record_id}/status",
        json={"status": "Approved"},
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    # Start maintenance
    response = client.patch(
        f"/api/v1/maintenance/{record_id}/status",
        json={"status": "In Progress"},
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "In Progress"

    # Verify vehicle status
    db_session.refresh(sample_vehicle)
    assert sample_vehicle.status == "In Shop"


def test_invalid_status_transition(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test invalid status transition is rejected."""
    payload = _maintenance_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/maintenance",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    record_id = create_response.json()["id"]

    # Try to jump from Pending to Completed (invalid)
    response = client.patch(
        f"/api/v1/maintenance/{record_id}/status",
        json={"status": "Completed"},
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    assert response.status_code == 400
    assert "cannot transition" in response.json()["error"]["message"].lower()


# ============================================================
# COMPLETE MAINTENANCE TESTS
# ============================================================

def test_complete_maintenance_success(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test completing maintenance restores vehicle."""
    # Create → Approve → Start
    payload = _maintenance_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/maintenance",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    record_id = create_response.json()["id"]

    client.patch(
        f"/api/v1/maintenance/{record_id}/status",
        json={"status": "Approved"},
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    client.patch(
        f"/api/v1/maintenance/{record_id}/status",
        json={"status": "In Progress"},
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    # Complete
    response = client.post(
        f"/api/v1/maintenance/{record_id}/complete",
        json={
            "completed_date": (date.today() + timedelta(days=7)).isoformat(),
            "actual_cost": 4800.00,
            "notes": "Maintenance completed successfully"
        },
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Completed"
    assert float(data["actual_cost"]) == 4800.00

    # Verify vehicle status restored
    db_session.refresh(sample_vehicle)
    assert sample_vehicle.status == "Available"


def test_complete_maintenance_wrong_status(
    client: TestClient,
    db_session: Session,
    fleet_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test completing maintenance from wrong status."""
    payload = _maintenance_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/maintenance",
        json=payload,
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )
    record_id = create_response.json()["id"]

    # Try to complete a Pending record (must be In Progress)
    response = client.post(
        f"/api/v1/maintenance/{record_id}/complete",
        json={
            "completed_date": date.today().isoformat(),
            "actual_cost": 4800.00
        },
        headers={"Authorization": f"Bearer {fleet_manager_token}"}
    )

    assert response.status_code == 400
    assert "in progress" in response.json()["error"]["message"].lower()
