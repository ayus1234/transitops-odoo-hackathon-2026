"""
Unit & Integration tests for Milestone 3 — Enterprise Intelligence & Analytics.
"""
import pytest
from datetime import datetime, date, timedelta
from uuid import UUID
from decimal import Decimal

from app.models.vehicle import Vehicle
from app.models.maintenance import Maintenance
from app.models.fuel import Fuel
from app.models.user import User
from app.models.role import Role
from app.models.expense import Expense
from app.models.telemetry import VehicleTelemetryLog
from app.schemas.telemetry import TelemetryRecord, TelemetryIngestBatchRequest
from app.services.analytics_service import AnalyticsService
from app.services.telemetry_service import TelemetryService


def test_fuel_theft_detection_algorithm(db_session):
    telemetry_service = TelemetryService(db_session)
    analytics_service = AnalyticsService(db_session)
    ts = int(datetime.now().timestamp() * 1000)

    vehicle = Vehicle(
        registration_number=f"FT-V1-{ts}",
        vehicle_name="Fuel Drain Test Truck",
        vehicle_type="Truck",
        capacity_kg=12000.00,
        fuel_type="Diesel",
        status="Available"
    )
    db_session.add(vehicle)
    db_session.commit()

    now = datetime.now()
    t1 = now - timedelta(minutes=10)
    t2 = now

    # Ping 1: 85% fuel at t1
    telemetry_service.ingest_telemetry_batch(TelemetryIngestBatchRequest(
        records=[
            TelemetryRecord(
                vehicle_id=UUID(str(vehicle.id)),
                latitude=19.0760,
                longitude=72.8777,
                speed_kmh=0.0,
                fuel_level_percent=85.0,
                timestamp=t1
            )
        ]
    ))

    # Ping 2: 60% fuel at t2 (25% drop in 10 mins while stationary!)
    telemetry_service.ingest_telemetry_batch(TelemetryIngestBatchRequest(
        records=[
            TelemetryRecord(
                vehicle_id=UUID(str(vehicle.id)),
                latitude=19.0760,
                longitude=72.8777,
                speed_kmh=0.0,
                fuel_level_percent=60.0,
                timestamp=t2
            )
        ]
    ))

    anomalies = analytics_service.detect_fuel_anomalies(days=1)
    v_anomalies = [a for a in anomalies if a.vehicle_id == UUID(str(vehicle.id))]

    assert len(v_anomalies) >= 1
    assert v_anomalies[0].anomaly_type == "FUEL_DRAIN_THEFT"
    assert v_anomalies[0].severity == "CRITICAL"
    assert v_anomalies[0].fuel_loss_liters == 75.0  # 25% of 300L tank


def test_fleet_health_score_calculation(db_session):
    analytics_service = AnalyticsService(db_session)
    ts = int(datetime.now().timestamp() * 1000)

    # High odometer truck with overdue maintenance
    vehicle = Vehicle(
        registration_number=f"HS-V2-{ts}",
        vehicle_name="Health Score Test Truck",
        vehicle_type="Truck",
        capacity_kg=15000.00,
        fuel_type="Diesel",
        current_odometer_km=Decimal("220000.00"),  # >200k km (-15 pts)
        status="Available"
    )
    db_session.add(vehicle)
    db_session.commit()

    maint = Maintenance(
        maintenance_number=f"MNT-HS-{ts}",
        vehicle_id=vehicle.id,
        maintenance_type="Overhaul",
        description="Engine overhaul",
        scheduled_date=date.today() - timedelta(days=10),
        status="Pending",  # Overdue because scheduled_date < today
        actual_cost=Decimal("1500.00")
    )
    db_session.add(maint)
    db_session.commit()

    health_scores = analytics_service.calculate_fleet_health_scores()
    v_health = next(h for h in health_scores if h.vehicle_id == UUID(str(vehicle.id)))

    # Expected Score: 100 - 15 (odometer) - 15 (overdue maint) = 70.0 (Warning)
    assert v_health.health_score == 70.0
    assert v_health.health_grade == "Warning"
    assert len(v_health.deductions) == 2


def test_tco_per_kilometer_calculation(db_session):
    analytics_service = AnalyticsService(db_session)
    ts = int(datetime.now().timestamp() * 1000)

    vehicle = Vehicle(
        registration_number=f"TCO-V3-{ts}",
        vehicle_name="TCO Test Van",
        vehicle_type="Van",
        capacity_kg=3000.00,
        fuel_type="Diesel",
        current_odometer_km=Decimal("10000.00"),
        status="Available"
    )
    db_session.add(vehicle)

    role = db_session.query(Role).first()
    if not role:
        role = Role(name="Admin", permissions={})
        db_session.add(role)
        db_session.commit()

    user = User(email=f"tco.user.{ts}@transitops.com", password_hash="hash", first_name="T", last_name="U", role_id=role.id, is_active=True)
    db_session.add(user)
    db_session.commit()

    fuel = Fuel(
        vehicle_id=vehicle.id,
        fuel_type="Diesel",
        quantity_liters=100.0,
        cost_per_liter=1.50,
        total_cost=150.00,
        odometer_reading=10000.0,
        refuel_date=datetime.now()
    )
    db_session.add(fuel)

    maint = Maintenance(
        maintenance_number=f"MNT-TCO-{ts}",
        vehicle_id=vehicle.id,
        maintenance_type="Oil Change",
        description="Regular oil change",
        scheduled_date=date.today(),
        status="Completed",
        actual_cost=Decimal("250.00")
    )
    db_session.add(maint)

    exp = Expense(
        vehicle_id=vehicle.id,
        expense_type="Toll",
        amount=Decimal("100.00"),
        expense_date=date.today(),
        description="Highway Tolls",
        recorded_by=user.id,
        status="Approved"
    )
    db_session.add(exp)
    db_session.commit()

    tco_list = analytics_service.calculate_tco_analytics()
    v_tco = next(t for t in tco_list if t.vehicle_id == UUID(str(vehicle.id)))

    # Fuel ($150) + Maint ($250) + Expense ($100) = $500 TCO
    # $500 / 10,000 km = $0.05 / km
    assert v_tco.total_tco == 500.0
    assert v_tco.cost_per_km == 0.05


def test_predictive_maintenance_wear_forecasting(db_session):
    analytics_service = AnalyticsService(db_session)
    ts = int(datetime.now().timestamp() * 1000)

    vehicle = Vehicle(
        registration_number=f"PM-V4-{ts}",
        vehicle_name="Predictive Test Vehicle",
        vehicle_type="Truck",
        capacity_kg=10000.00,
        fuel_type="Diesel",
        current_odometer_km=Decimal("9500.00"),  # 95% engine oil wear
        status="Available"
    )
    db_session.add(vehicle)
    db_session.commit()

    forecasts = analytics_service.forecast_predictive_maintenance()
    v_fc = next(f for f in forecasts if f.vehicle_id == UUID(str(vehicle.id)))

    oil_component = next(c for c in v_fc.components if "Oil" in c.component)
    assert oil_component.current_wear_percent == 95.0
    assert oil_component.urgency == "URGENT"
