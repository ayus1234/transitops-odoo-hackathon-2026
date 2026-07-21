"""
Test expense endpoints.
"""
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal
from uuid import uuid4

from app.models.role import Role
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.expense import Expense
from app.core.security import get_password_hash


@pytest.fixture
def expense_manager_user(db_session: Session) -> User:
    """Create Expense Manager user for testing."""
    role = Role(
        name="Finance Manager",
        permissions={
            "vehicles": ["read"],
            "expenses": ["read", "create", "update", "delete"]
        }
    )
    db_session.add(role)
    db_session.commit()

    user = User(
        email="finance@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="Finance",
        last_name="Manager",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def expense_manager_token(client: TestClient, expense_manager_user: User) -> str:
    """Get JWT token for Expense Manager."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "finance@transitops.com",
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


def _expense_payload(vehicle_id=None):
    """Helper to build an expense creation payload."""
    payload = {
        "expense_type": "Toll",
        "amount": 500.00,
        "expense_date": date.today().isoformat(),
        "description": "Highway toll",
        "vendor_name": "NHAI"
    }
    if vehicle_id:
        payload["vehicle_id"] = str(vehicle_id)
    return payload


# ============================================================
# CREATE EXPENSE TESTS
# ============================================================

def test_create_expense_success(
    client: TestClient,
    db_session: Session,
    expense_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test successful expense creation."""
    payload = _expense_payload(sample_vehicle.id)

    response = client.post(
        "/api/v1/expenses",
        json=payload,
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["expense_type"] == "Toll"
    assert data["status"] == "Pending"
    assert data["vehicle"]["registration_number"] == "DL-01-AB-1234"


def test_create_expense_no_relation(
    client: TestClient,
    db_session: Session,
    expense_manager_token: str
):
    """Test creating expense with no linked vehicle/trip/maintenance fails."""
    payload = _expense_payload()

    response = client.post(
        "/api/v1/expenses",
        json=payload,
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )

    assert response.status_code == 400
    assert "least one entity" in response.json()["error"]["message"].lower()


def test_create_expense_invalid_type(
    client: TestClient,
    db_session: Session,
    expense_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test creating expense with invalid type."""
    payload = _expense_payload(sample_vehicle.id)
    payload["expense_type"] = "InvalidType"

    response = client.post(
        "/api/v1/expenses",
        json=payload,
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )

    assert response.status_code == 422


def test_create_expense_invalid_amount(
    client: TestClient,
    db_session: Session,
    expense_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test creating expense with negative amount."""
    payload = _expense_payload(sample_vehicle.id)
    payload["amount"] = -50.00

    response = client.post(
        "/api/v1/expenses",
        json=payload,
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )

    assert response.status_code == 422


def test_create_expense_future_date(
    client: TestClient,
    db_session: Session,
    expense_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test creating expense with future date."""
    payload = _expense_payload(sample_vehicle.id)
    payload["expense_date"] = (date.today() + timedelta(days=5)).isoformat()

    response = client.post(
        "/api/v1/expenses",
        json=payload,
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )

    assert response.status_code == 400
    assert "future" in response.json()["error"]["message"].lower()


# ============================================================
# LIST / GET TESTS
# ============================================================

def test_list_expenses(
    client: TestClient,
    db_session: Session,
    expense_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test listing expenses."""
    payload = _expense_payload(sample_vehicle.id)
    client.post(
        "/api/v1/expenses",
        json=payload,
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )

    response = client.get(
        "/api/v1/expenses",
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) > 0


def test_get_expense_by_id(
    client: TestClient,
    db_session: Session,
    expense_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test getting expense by ID."""
    payload = _expense_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/expenses",
        json=payload,
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )
    record_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/expenses/{record_id}",
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )

    assert response.status_code == 200
    assert response.json()["id"] == record_id


# ============================================================
# UPDATE TESTS
# ============================================================

def test_update_expense(
    client: TestClient,
    db_session: Session,
    expense_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test updating a pending expense."""
    payload = _expense_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/expenses",
        json=payload,
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )
    record_id = create_response.json()["id"]

    update_data = {
        "amount": 750.00,
        "description": "Updated toll"
    }

    response = client.put(
        f"/api/v1/expenses/{record_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )

    assert response.status_code == 200
    assert float(response.json()["amount"]) == 750.00


def test_update_approved_expense_fails(
    client: TestClient,
    db_session: Session,
    expense_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test updating an approved expense is blocked."""
    payload = _expense_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/expenses",
        json=payload,
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )
    record_id = create_response.json()["id"]

    # Approve it
    client.patch(
        f"/api/v1/expenses/{record_id}/approve",
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )

    # Try to update
    response = client.put(
        f"/api/v1/expenses/{record_id}",
        json={"amount": 1000.00},
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )

    assert response.status_code == 400
    assert "approved" in response.json()["error"]["message"].lower()


# ============================================================
# STATUS LIFECYCLE TESTS
# ============================================================

def test_approve_expense(
    client: TestClient,
    db_session: Session,
    expense_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test approving an expense."""
    payload = _expense_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/expenses",
        json=payload,
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )
    record_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/expenses/{record_id}/approve",
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Approved"
    assert data["approver"]["first_name"] == "Finance"


def test_reject_expense(
    client: TestClient,
    db_session: Session,
    expense_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test rejecting an expense."""
    payload = _expense_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/expenses",
        json=payload,
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )
    record_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/expenses/{record_id}/reject",
        json={"reason": "Duplicate entry"},
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Rejected"


# ============================================================
# DELETE TESTS
# ============================================================

def test_delete_expense(
    client: TestClient,
    db_session: Session,
    expense_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test deleting a pending expense."""
    payload = _expense_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/expenses",
        json=payload,
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )
    record_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/expenses/{record_id}",
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )

    assert response.status_code == 200


def test_delete_approved_expense_fails(
    client: TestClient,
    db_session: Session,
    expense_manager_token: str,
    sample_vehicle: Vehicle
):
    """Test deleting an approved expense fails."""
    payload = _expense_payload(sample_vehicle.id)
    create_response = client.post(
        "/api/v1/expenses",
        json=payload,
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )
    record_id = create_response.json()["id"]

    # Approve it
    client.patch(
        f"/api/v1/expenses/{record_id}/approve",
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )

    # Try to delete
    response = client.delete(
        f"/api/v1/expenses/{record_id}",
        headers={"Authorization": f"Bearer {expense_manager_token}"}
    )

    assert response.status_code == 400
    assert "approved" in response.json()["error"]["message"].lower()
