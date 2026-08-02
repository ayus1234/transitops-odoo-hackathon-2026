"""
Tests for Vehicle 360 profile and lifecycle management.
These tests validate the V2 extensions without modifying baseline tests.
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.role import Role
from app.models.user import User
from app.models.vehicle import Vehicle, VEHICLE_STATUS_TRANSITIONS
from app.core.security import get_password_hash


@pytest.fixture
def fleet_manager_user_360(db_session: Session) -> User:
    """Create Fleet Manager user for Vehicle 360 testing."""
    role = Role(
        name="Fleet Manager V360",
        permissions={"vehicles": ["read", "create", "update", "delete"]}
    )
    db_session.add(role)
    db_session.commit()

    user = User(
        email="manager360@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="Fleet",
        last_name="Manager360",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def fleet_manager_token_360(client: TestClient, fleet_manager_user_360: User) -> str:
    """Get JWT token for Fleet Manager 360."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "manager360@transitops.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def vehicle_360(db_session: Session) -> Vehicle:
    """Create a vehicle with Vehicle 360 fields populated."""
    vehicle = Vehicle(
        registration_number="V360-TEST-001",
        vehicle_name="Tata Ace Gold V360",
        vehicle_type="Truck",
        manufacturer="Tata Motors",
        model="Ace Gold",
        variant="Plus",
        year=2024,
        body_type="Truck",
        powertrain="ICE",
        capacity_kg=Decimal("2000.00"),
        seating_capacity=2,
        fuel_type="Diesel",
        current_odometer_km=Decimal("12500.00"),
        engine_hours=Decimal("450.00"),
        vin="MAT467891ABC12345",
        ownership_type="Owned",
        acquisition_cost=Decimal("850000.00"),
        acquisition_date=date(2024, 1, 15),
        insurance_expiry=date(2027, 1, 15),
        notes="Fleet 360 test vehicle",
        status="Available"
    )
    db_session.add(vehicle)
    db_session.commit()
    db_session.refresh(vehicle)
    return vehicle


# ── Vehicle 360 Profile Creation Tests ──

def test_create_vehicle_with_360_fields(
    client: TestClient,
    db_session: Session,
    fleet_manager_token_360: str
):
    """Test creating a vehicle with Vehicle 360 extended fields."""
    vehicle_data = {
        "registration_number": "V360-CREATE-001",
        "vehicle_name": "Mahindra Bolero Maxi 360",
        "vehicle_type": "Pickup",
        "manufacturer": "Mahindra",
        "model": "Bolero Maxi Truck",
        "variant": "Plus",
        "year": 2025,
        "body_type": "Pickup",
        "powertrain": "ICE",
        "capacity_kg": 1500.00,
        "seating_capacity": 3,
        "fuel_type": "Diesel",
        "current_odometer_km": 0.00,
        "engine_hours": 0.00,
        "vin": "MAH123456789VTEST",
        "ownership_type": "Owned",
        "acquisition_cost": 750000.00,
        "acquisition_date": "2025-01-10",
        "insurance_expiry": "2027-01-10",
        "notes": "Brand new acquisition for V360 testing"
    }

    response = client.post(
        "/api/v1/vehicles",
        json=vehicle_data,
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["registration_number"] == "V360-CREATE-001"
    assert data["vin"] == "MAH123456789VTEST"
    assert data["body_type"] == "Pickup"
    assert data["powertrain"] == "ICE"
    assert data["ownership_type"] == "Owned"
    assert data["variant"] == "Plus"
    assert data["seating_capacity"] == 3
    assert data["status"] == "Available"


def test_create_vehicle_with_lease_info(
    client: TestClient,
    db_session: Session,
    fleet_manager_token_360: str
):
    """Test creating a leased vehicle with lease details."""
    vehicle_data = {
        "registration_number": "V360-LEASE-001",
        "vehicle_name": "Leased EV Van",
        "vehicle_type": "Van",
        "capacity_kg": 2000.00,
        "fuel_type": "Electric",
        "powertrain": "Electric",
        "ownership_type": "Leased",
        "lease_provider": "FleetLease India Pvt Ltd",
        "lease_start_date": "2025-01-01",
        "lease_end_date": "2028-12-31",
        "monthly_lease_cost": 35000.00,
    }

    response = client.post(
        "/api/v1/vehicles",
        json=vehicle_data,
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["ownership_type"] == "Leased"
    assert data["lease_provider"] == "FleetLease India Pvt Ltd"
    assert float(data["monthly_lease_cost"]) == 35000.00


def test_create_vehicle_duplicate_vin(
    client: TestClient,
    db_session: Session,
    fleet_manager_token_360: str,
    vehicle_360: Vehicle
):
    """Test that duplicate VIN is rejected."""
    vehicle_data = {
        "registration_number": "V360-DUP-VIN-001",
        "vehicle_name": "Duplicate VIN Vehicle",
        "vehicle_type": "Truck",
        "capacity_kg": 5000.00,
        "fuel_type": "Diesel",
        "vin": vehicle_360.vin,  # Same VIN as existing vehicle
    }

    response = client.post(
        "/api/v1/vehicles",
        json=vehicle_data,
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    assert response.status_code == 400
    assert "vin" in response.json()["error"]["message"].lower()


def test_create_vehicle_invalid_body_type(
    client: TestClient,
    fleet_manager_token_360: str
):
    """Test that invalid body type is rejected by schema validation."""
    vehicle_data = {
        "registration_number": "V360-INVALID-001",
        "vehicle_name": "Invalid Body",
        "vehicle_type": "Truck",
        "capacity_kg": 5000.00,
        "fuel_type": "Diesel",
        "body_type": "Spaceship",
    }

    response = client.post(
        "/api/v1/vehicles",
        json=vehicle_data,
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    assert response.status_code == 422


def test_create_vehicle_invalid_powertrain(
    client: TestClient,
    fleet_manager_token_360: str
):
    """Test that invalid powertrain is rejected by schema validation."""
    vehicle_data = {
        "registration_number": "V360-INVALID-002",
        "vehicle_name": "Invalid Powertrain",
        "vehicle_type": "Truck",
        "capacity_kg": 5000.00,
        "fuel_type": "Diesel",
        "powertrain": "Nuclear",
    }

    response = client.post(
        "/api/v1/vehicles",
        json=vehicle_data,
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    assert response.status_code == 422


# ── Vehicle 360 Profile Endpoint Tests ──

def test_get_vehicle_360_profile(
    client: TestClient,
    fleet_manager_token_360: str,
    vehicle_360: Vehicle
):
    """Test GET /vehicles/{id}/360 returns full profile with lifecycle transitions."""
    response = client.get(
        f"/api/v1/vehicles/{vehicle_360.id}/360",
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Vehicle data present
    assert data["vehicle"]["registration_number"] == "V360-TEST-001"
    assert data["vehicle"]["vin"] == "MAT467891ABC12345"
    assert data["vehicle"]["body_type"] == "Truck"
    assert data["vehicle"]["powertrain"] == "ICE"
    assert data["vehicle"]["ownership_type"] == "Owned"

    # Lifecycle transitions present
    assert "allowed_transitions" in data
    assert isinstance(data["allowed_transitions"], list)
    # Available vehicle should have multiple transitions
    assert len(data["allowed_transitions"]) > 0
    assert "Retired" in data["allowed_transitions"]


def test_get_vehicle_360_not_found(
    client: TestClient,
    fleet_manager_token_360: str
):
    """Test GET /vehicles/{id}/360 for non-existent vehicle returns error."""
    import uuid
    fake_id = uuid.uuid4()
    response = client.get(
        f"/api/v1/vehicles/{fake_id}/360",
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    # NotFoundError is mapped to 400 by the existing global exception handler
    assert response.status_code == 400
    assert "not found" in response.json()["error"]["message"].lower()


# ── Lifecycle Status Transition Tests ──

def test_lifecycle_available_to_maintenance(
    client: TestClient,
    fleet_manager_token_360: str,
    vehicle_360: Vehicle
):
    """Test lifecycle: Available → Maintenance."""
    response = client.patch(
        f"/api/v1/vehicles/{vehicle_360.id}/status",
        json={
            "new_status": "Maintenance",
            "reason": "Scheduled preventive maintenance"
        },
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Maintenance"


def test_lifecycle_available_to_retired(
    client: TestClient,
    db_session: Session,
    fleet_manager_token_360: str
):
    """Test lifecycle: Available → Retired with retired_date."""
    vehicle = Vehicle(
        registration_number="V360-RETIRE-001",
        vehicle_name="Old Truck",
        vehicle_type="Truck",
        capacity_kg=Decimal("8000.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("500000.00"),
        status="Available"
    )
    db_session.add(vehicle)
    db_session.commit()

    response = client.patch(
        f"/api/v1/vehicles/{vehicle.id}/status",
        json={
            "new_status": "Retired",
            "reason": "End of service life",
            "retired_date": "2026-07-28"
        },
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Retired"
    assert data["retired_date"] == "2026-07-28"


def test_lifecycle_retired_to_sold(
    client: TestClient,
    db_session: Session,
    fleet_manager_token_360: str
):
    """Test lifecycle: Retired → Sold with sale_price."""
    vehicle = Vehicle(
        registration_number="V360-SELL-001",
        vehicle_name="Truck for Sale",
        vehicle_type="Truck",
        capacity_kg=Decimal("10000.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("400000.00"),
        status="Retired",
        retired_date=date(2026, 6, 1)
    )
    db_session.add(vehicle)
    db_session.commit()

    response = client.patch(
        f"/api/v1/vehicles/{vehicle.id}/status",
        json={
            "new_status": "Sold",
            "reason": "Sold to dealer",
            "sale_price": 250000.00
        },
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Sold"
    assert float(data["sale_price"]) == 250000.00


def test_lifecycle_invalid_transition_sold_to_available(
    client: TestClient,
    db_session: Session,
    fleet_manager_token_360: str
):
    """Test that sold vehicle cannot transition back to Available."""
    vehicle = Vehicle(
        registration_number="V360-SOLD-001",
        vehicle_name="Sold Truck",
        vehicle_type="Truck",
        capacity_kg=Decimal("10000.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("450000.00"),
        status="Sold"
    )
    db_session.add(vehicle)
    db_session.commit()

    response = client.patch(
        f"/api/v1/vehicles/{vehicle.id}/status",
        json={
            "new_status": "Available",
            "reason": "Try to reactivate"
        },
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    assert response.status_code == 400
    assert "cannot transition" in response.json()["error"]["message"].lower()


def test_lifecycle_manual_on_trip_blocked(
    client: TestClient,
    fleet_manager_token_360: str,
    vehicle_360: Vehicle
):
    """Test that manual transition to On Trip is blocked via generic update."""
    response = client.put(
        f"/api/v1/vehicles/{vehicle_360.id}",
        json={"status": "On Trip"},
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    assert response.status_code == 400
    assert "trip dispatch" in response.json()["error"]["message"].lower()


def test_lifecycle_maintenance_to_available(
    client: TestClient,
    db_session: Session,
    fleet_manager_token_360: str
):
    """Test lifecycle: Maintenance → Available (return to service)."""
    vehicle = Vehicle(
        registration_number="V360-MAINT-RET-001",
        vehicle_name="Maintenance Return",
        vehicle_type="Van",
        capacity_kg=Decimal("3000.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("75000.00"),
        status="Maintenance"
    )
    db_session.add(vehicle)
    db_session.commit()

    response = client.patch(
        f"/api/v1/vehicles/{vehicle.id}/status",
        json={
            "new_status": "Available",
            "reason": "Maintenance completed"
        },
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Available"


def test_lifecycle_invalid_status_value(
    client: TestClient,
    fleet_manager_token_360: str,
    vehicle_360: Vehicle
):
    """Test that invalid status value is rejected by schema validation."""
    response = client.patch(
        f"/api/v1/vehicles/{vehicle_360.id}/status",
        json={
            "new_status": "Flying",
        },
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    assert response.status_code == 422


# ── Vehicle 360 Update Tests ──

def test_update_vehicle_360_fields(
    client: TestClient,
    fleet_manager_token_360: str,
    vehicle_360: Vehicle
):
    """Test updating Vehicle 360 extended fields."""
    update_data = {
        "variant": "Plus XL",
        "engine_hours": 500.00,
        "notes": "Updated notes after service"
    }

    response = client.put(
        f"/api/v1/vehicles/{vehicle_360.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["variant"] == "Plus XL"
    assert float(data["engine_hours"]) == 500.00
    assert data["notes"] == "Updated notes after service"


# ── VIN Search Test ──

def test_search_vehicles_by_vin(
    client: TestClient,
    fleet_manager_token_360: str,
    vehicle_360: Vehicle
):
    """Test searching vehicles by VIN."""
    response = client.get(
        f"/api/v1/vehicles?search={vehicle_360.vin[:8]}",
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1
    found = any(v["registration_number"] == "V360-TEST-001" for v in data["data"])
    assert found


# ── Delete Protection for New States ──

def test_delete_vehicle_in_maintenance_blocked(
    client: TestClient,
    db_session: Session,
    fleet_manager_token_360: str
):
    """Test that vehicles in Maintenance state cannot be deleted."""
    vehicle = Vehicle(
        registration_number="V360-DEL-MAINT-001",
        vehicle_name="Maintenance Truck",
        vehicle_type="Truck",
        capacity_kg=Decimal("8000.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("200000.00"),
        status="Maintenance"
    )
    db_session.add(vehicle)
    db_session.commit()

    response = client.delete(
        f"/api/v1/vehicles/{vehicle.id}",
        headers={"Authorization": f"Bearer {fleet_manager_token_360}"}
    )

    assert response.status_code == 400
    assert "cannot delete" in response.json()["error"]["message"].lower()


# ── Model-Level Lifecycle Validation Tests ──

def test_model_can_transition_to_valid():
    """Test Vehicle.can_transition_to() for valid transitions."""
    vehicle = Vehicle(status="Available")
    assert vehicle.can_transition_to("Maintenance") is True
    assert vehicle.can_transition_to("Retired") is True
    assert vehicle.can_transition_to("Inactive") is True


def test_model_can_transition_to_invalid():
    """Test Vehicle.can_transition_to() for invalid transitions."""
    vehicle = Vehicle(status="Sold")
    assert vehicle.can_transition_to("Available") is False
    assert vehicle.can_transition_to("Active") is False


def test_model_get_allowed_transitions():
    """Test Vehicle.get_allowed_transitions() returns correct list."""
    vehicle = Vehicle(status="Retired")
    allowed = vehicle.get_allowed_transitions()
    assert allowed == ["Sold"]

    vehicle2 = Vehicle(status="Sold")
    allowed2 = vehicle2.get_allowed_transitions()
    assert allowed2 == []


def test_model_all_statuses_have_transitions():
    """Verify every status in the transition map is defined."""
    for status in VEHICLE_STATUS_TRANSITIONS:
        vehicle = Vehicle(status=status)
        transitions = vehicle.get_allowed_transitions()
        assert isinstance(transitions, list)
