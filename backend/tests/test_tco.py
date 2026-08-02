"""
Tests for Total Cost of Ownership (TCO) calculation feature.
"""
import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.role import Role
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.fuel import Fuel
from app.models.maintenance import Maintenance
from app.models.expense import Expense
from app.core.security import get_password_hash


@pytest.fixture
def tco_user(db_session: Session) -> User:
    """Create user for TCO testing."""
    role = Role(
        name="Fleet Manager TCO",
        permissions={"vehicles": ["read", "create", "update", "delete"]}
    )
    db_session.add(role)
    db_session.commit()

    user = User(
        email="tco_manager@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="TCO",
        last_name="Manager",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def tco_token(client: TestClient, tco_user: User) -> str:
    """Get JWT token for TCO tester."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "tco_manager@transitops.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def tco_vehicle(db_session: Session, tco_user: User) -> Vehicle:
    """Create vehicle with costs (fuel, maintenance, expenses) for TCO calculation."""
    vehicle = Vehicle(
        registration_number="TCO-TEST-001",
        vehicle_name="TCO Calculation Truck",
        vehicle_type="Truck",
        capacity_kg=Decimal("12000.00"),
        fuel_type="Diesel",
        current_odometer_km=Decimal("10000.00"),
        acquisition_cost=Decimal("2000000.00"),
        monthly_lease_cost=Decimal("0.00"),
        status="Available"
    )
    db_session.add(vehicle)
    db_session.commit()

    # 1. Add fuel logs (15,000 cost)
    fuel_log = Fuel(
        vehicle_id=vehicle.id,
        fuel_type="Diesel",
        quantity_liters=Decimal("150.00"),
        cost_per_liter=Decimal("100.00"),
        total_cost=Decimal("15000.00"),
        odometer_reading=Decimal("10000.00"),
        recorded_by=tco_user.id
    )
    db_session.add(fuel_log)

    # 2. Add completed maintenance (25,000 cost)
    maint_log = Maintenance(
        maintenance_number="MAINT-TCO-001",
        vehicle_id=vehicle.id,
        maintenance_type="Engine Service",
        description="Routine maintenance",
        priority="Medium",
        scheduled_date=date.today(),
        actual_cost=Decimal("25000.00"),
        status="Completed",
        created_by=tco_user.id
    )
    db_session.add(maint_log)

    # 3. Add approved expense (5,000 cost)
    expense = Expense(
        expense_type="Toll",
        amount=Decimal("5000.00"),
        expense_date=date.today(),
        description="Highway toll charges",
        status="Approved",
        vehicle_id=vehicle.id,
        recorded_by=tco_user.id
    )
    db_session.add(expense)
    db_session.commit()
    db_session.refresh(vehicle)
    return vehicle


def test_calculate_vehicle_tco(
    client: TestClient,
    tco_token: str,
    tco_vehicle: Vehicle
):
    """Test GET /vehicles/{id}/tco endpoint returns correct cost aggregation."""
    response = client.get(
        f"/api/v1/vehicles/{tco_vehicle.id}/tco",
        headers={"Authorization": f"Bearer {tco_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    tco_data = data["data"]
    assert tco_data["vehicle_id"] == str(tco_vehicle.id)
    assert tco_data["current_odometer_km"] == 10000.00

    costs = tco_data["cost_breakdown"]
    assert costs["acquisition_cost"] == 2000000.00
    assert costs["total_fuel_cost"] == 15000.00
    assert costs["total_maintenance_cost"] == 25000.00
    assert costs["total_other_expenses"] == 5000.00
    assert costs["total_operating_cost"] == 45000.00  # 15k + 25k + 5k
    assert costs["total_tco"] == 2045000.00          # 2M + 45k

    unit = tco_data["unit_metrics"]
    assert unit["cost_per_km"] == 4.5  # 45,000 / 10,000 km = 4.5 per km
    assert unit["fuel_cost_per_km"] == 1.5
    assert unit["maintenance_cost_per_km"] == 2.5


def test_tco_for_nonexistent_vehicle(
    client: TestClient,
    tco_token: str
):
    """Test TCO endpoint for non-existent vehicle returns error."""
    import uuid
    fake_id = uuid.uuid4()

    response = client.get(
        f"/api/v1/vehicles/{fake_id}/tco",
        headers={"Authorization": f"Bearer {tco_token}"}
    )

    assert response.status_code == 400
    assert "not found" in response.json()["error"]["message"].lower()
