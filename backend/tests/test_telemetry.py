"""
Unit & Integration tests for Milestone 2 — Connected Fleet Telemetry & IoT.
"""
import pytest
from datetime import datetime, date, timedelta
from uuid import UUID
from decimal import Decimal

from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.user import User
from app.models.role import Role
from app.models.job import Job
from app.models.trip import Trip
from app.models.trip_stop import TripStop
from app.schemas.telemetry import TelemetryRecord, TelemetryIngestBatchRequest
from app.services.telemetry_service import TelemetryService
from app.services.audit_event_service import AuditEventService


def test_telemetry_batch_ingestion_and_vehicle_position_update(db_session):
    telemetry_service = TelemetryService(db_session)
    ts = int(datetime.now().timestamp() * 1000)

    # 1. Create Vehicle
    vehicle = Vehicle(
        registration_number=f"TEL-V1-{ts}",
        vehicle_name="Telemetry Test Truck",
        vehicle_type="Truck",
        capacity_kg=15000.00,
        fuel_type="Diesel",
        status="Available"
    )
    db_session.add(vehicle)
    db_session.commit()

    # 2. Prepare Batch Ingestion
    batch_req = TelemetryIngestBatchRequest(
        device_id=f"DEV-{ts}",
        records=[
            TelemetryRecord(
                vehicle_id=UUID(str(vehicle.id)),
                latitude=19.0760,
                longitude=72.8777,
                speed_kmh=45.5,
                heading=180.0,
                ignition=True,
                fuel_level_percent=85.0,
                odometer_km=12500.0
            )
        ]
    )

    res = telemetry_service.ingest_telemetry_batch(batch_req)

    assert res.records_processed == 1

    # Verify vehicle state updated
    db_session.refresh(vehicle)
    assert float(str(vehicle.latitude)) == 19.0760
    assert float(str(vehicle.longitude)) == 72.8777
    assert float(str(vehicle.current_odometer_km)) == 12500.0


def test_telemetry_speeding_alert_and_geofence_arrival(db_session):
    telemetry_service = TelemetryService(db_session)
    audit_service = AuditEventService(db_session)

    role = db_session.query(Role).first()
    if not role:
        role = Role(name="Driver", permissions={})
        db_session.add(role)
        db_session.commit()

    ts = int(datetime.now().timestamp() * 1000)

    vehicle = Vehicle(registration_number=f"TEL-V2-{ts}", vehicle_name="Speed Truck", vehicle_type="Truck", capacity_kg=10000.00, fuel_type="Diesel", status="On Trip")
    db_session.add(vehicle)

    user = User(email=f"tel.driver.{ts}@transitops.com", password_hash="hash", first_name="T", last_name="D", role_id=role.id, is_active=True)
    db_session.add(user)
    db_session.commit()

    driver = Driver(user_id=user.id, license_number=f"LIC-TEL-{ts}", license_category="C", license_issue_date=date(2020, 1, 1), date_of_birth=date(1990, 1, 1), status="On Trip", license_expiry_date=date(2035, 1, 1))
    db_session.add(driver)
    db_session.commit()

    now = datetime.now()
    trip = Trip(trip_number=f"TRP-TEL-{ts}", vehicle_id=vehicle.id, driver_id=driver.id, source="A", destination="B", cargo_weight_kg=Decimal("2000.0"), planned_distance_km=Decimal("80.0"), planned_departure=now, planned_arrival=now + timedelta(hours=2), status="Dispatched")
    db_session.add(trip)
    db_session.commit()

    # Target Stop: Mumbai Airport (19.0896, 72.8656)
    stop = TripStop(
        trip_id=trip.id,
        sequence=1,
        location_name="Airport Cargo Terminal",
        latitude=Decimal("19.0896"),
        longitude=Decimal("72.8656"),
        stop_type="Delivery",
        status="Pending"
    )
    db_session.add(stop)
    db_session.commit()

    # Telemetry Ping: Over-speeding at 98.0 km/h AND located at (19.0897, 72.8657) — ~15m from stop!
    batch_req = TelemetryIngestBatchRequest(
        records=[
            TelemetryRecord(
                vehicle_id=UUID(str(vehicle.id)),
                latitude=19.0897,
                longitude=72.8657,
                speed_kmh=98.0,  # >80 km/h speeding limit
                heading=90.0,
                ignition=True
            )
        ]
    )

    res = telemetry_service.ingest_telemetry_batch(batch_req)

    assert res.records_processed == 1
    assert res.alerts_triggered >= 2  # Speeding + Geofence Enter

    # Verify stop status auto-transitioned to Arrived
    db_session.refresh(stop)
    assert stop.status == "Arrived"

    # Verify Audit Events logged
    timeline = audit_service.get_trip_timeline(UUID(str(trip.id)))
    event_types = [e.event_type for e in timeline.events]
    assert "SPEEDING_ALERT" in event_types
    assert "GEOFENCE_ENTER" in event_types


def test_live_fleet_positions_and_heartbeat_online_status(db_session):
    telemetry_service = TelemetryService(db_session)
    ts = int(datetime.now().timestamp() * 1000)

    vehicle = Vehicle(
        registration_number=f"TEL-V3-{ts}",
        vehicle_name="Live Fleet Bus",
        vehicle_type="Bus",
        capacity_kg=5000.00,
        fuel_type="CNG",
        status="Available"
    )
    db_session.add(vehicle)
    db_session.commit()

    # Ping telemetry
    telemetry_service.ingest_telemetry_batch(TelemetryIngestBatchRequest(
        records=[
            TelemetryRecord(
                vehicle_id=UUID(str(vehicle.id)),
                latitude=18.5204,
                longitude=73.8567,
                speed_kmh=30.0
            )
        ]
    ))

    live_fleet = telemetry_service.get_live_fleet_positions()
    v_stat = next(f for f in live_fleet if f.vehicle_id == UUID(str(vehicle.id)))

    assert v_stat.registration_number == f"TEL-V3-{ts}"
    assert v_stat.is_online is True
    assert v_stat.latitude == 18.5204
    assert v_stat.longitude == 73.8567
    assert v_stat.speed_kmh == 30.0
