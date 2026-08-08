"""
Unit tests for Priority 3 — Proof of Delivery (POD) Workflow.
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
from app.schemas.pod import PODSubmissionRequest
from app.services.pod_service import PODService
from app.schemas.job import JobCreate
from app.services.job_service import JobService


def test_submit_pod_geofence_verified_and_job_transition(db_session):
    pod_service = PODService(db_session)
    job_service = JobService(db_session)

    role = db_session.query(Role).first()
    if not role:
        role = Role(name="Driver", permissions={})
        db_session.add(role)
        db_session.commit()

    ts = int(datetime.now().timestamp() * 1000)

    # 1. Create Vehicle, Driver & Job
    vehicle = Vehicle(
        registration_number=f"POD-V-{ts}",
        vehicle_name="POD Delivery Van",
        vehicle_type="Van",
        capacity_kg=5000.00,
        fuel_type="Diesel",
        status="On Trip"
    )
    db_session.add(vehicle)

    user = User(
        email=f"pod.driver.{ts}@transitops.com",
        password_hash="hash",
        first_name="POD",
        last_name="Driver",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    driver = Driver(
        user_id=user.id,
        license_number=f"LIC-POD-{ts}",
        license_category="Commercial",
        license_issue_date=date(2020, 1, 1),
        date_of_birth=date(1990, 1, 1),
        status="On Trip",
        license_expiry_date=date(2035, 1, 1)
    )
    db_session.add(driver)
    db_session.commit()

    job = job_service.create_job(JobCreate(
        customer_name=f"POD Customer {ts}",
        pickup_address="BKC Mumbai",
        delivery_address="Phugewadi Pune",
        cargo_weight_kg=2500.00
    ))
    db_session.query(Job).filter(Job.id == job.id).update({"status": "In Transit"})
    db_session.commit()

    now = datetime.now()
    trip = Trip(
        trip_number=f"TRP-POD-{ts}",
        vehicle_id=vehicle.id,
        driver_id=driver.id,
        source="BKC Mumbai",
        destination="Phugewadi Pune",
        cargo_weight_kg=Decimal("2500.00"),
        planned_distance_km=Decimal("140.0"),
        planned_departure=now,
        planned_arrival=now + timedelta(hours=3),
        status="Dispatched"
    )
    db_session.add(trip)
    db_session.commit()

    # Create Delivery Stop linked to Job
    # BKC Coordinates: 19.0657, 72.8688
    stop = TripStop(
        trip_id=trip.id,
        sequence=2,
        location_name="Phugewadi Depot",
        latitude=Decimal("19.0657"),
        longitude=Decimal("72.8688"),
        stop_type="Delivery",
        job_id=job.id,
        status="Pending"
    )
    db_session.add(stop)
    db_session.commit()

    # Submit POD (driver is at 19.0658, 72.8689 — ~15 meters away)
    req = PODSubmissionRequest(
        receiver_name="Aarav Sharma",
        receiver_phone="+91 9876543210",
        signature_base64="data:image/svg+xml;base64,PHN2Zz48L3N2Zz4=",
        photo_url="https://transitops.s3.amazonaws.com/pod/photo_123.jpg",
        submitted_latitude=19.0658,
        submitted_longitude=72.8689,
        notes="Received in perfect condition"
    )

    res = pod_service.submit_proof_of_delivery(UUID(str(stop.id)), req)

    assert res.stop_id == UUID(str(stop.id))
    assert res.is_geofence_verified is True
    assert res.geo_distance_offset_meters < 50.0
    assert res.proof_of_delivery["receiver_name"] == "Aarav Sharma"

    # Verify DB updates
    db_session.refresh(stop)
    assert stop.status == "Completed"
    assert stop.proof_of_delivery["is_geofence_verified"] is True

    # Verify Job auto-transition to Delivered
    refreshed_job = db_session.query(Job).filter(Job.id == job.id).first()
    assert refreshed_job.status == "Delivered"


def test_submit_pod_geofence_out_of_bounds(db_session):
    pod_service = PODService(db_session)

    role = db_session.query(Role).first()
    if not role:
        role = Role(name="Driver", permissions={})
        db_session.add(role)
        db_session.commit()

    ts = int(datetime.now().timestamp() * 1000)

    vehicle = Vehicle(registration_number=f"POD-V2-{ts}", vehicle_name="Truck", vehicle_type="Truck", capacity_kg=10000.00, fuel_type="Diesel", status="On Trip")
    db_session.add(vehicle)

    user = User(email=f"pod.driver2.{ts}@transitops.com", password_hash="hash", first_name="P", last_name="D", role_id=role.id, is_active=True)
    db_session.add(user)
    db_session.commit()

    driver = Driver(user_id=user.id, license_number=f"LIC-P2-{ts}", license_category="C", license_issue_date=date(2020, 1, 1), date_of_birth=date(1990, 1, 1), status="On Trip", license_expiry_date=date(2035, 1, 1))
    db_session.add(driver)
    db_session.commit()

    now = datetime.now()
    trip = Trip(trip_number=f"TRP-P2-{ts}", vehicle_id=vehicle.id, driver_id=driver.id, source="A", destination="B", cargo_weight_kg=Decimal("1000.0"), planned_distance_km=Decimal("50.0"), planned_departure=now, planned_arrival=now + timedelta(hours=2), status="Dispatched")
    db_session.add(trip)
    db_session.commit()

    # Stop location: Mumbai BKC (19.0657, 72.8688)
    stop = TripStop(
        trip_id=trip.id,
        sequence=1,
        location_name="BKC Drop",
        latitude=Decimal("19.0657"),
        longitude=Decimal("72.8688"),
        stop_type="Delivery",
        status="Pending"
    )
    db_session.add(stop)
    db_session.commit()

    # Driver submits POD from Pune (18.5204, 73.8567) -> ~120 km away!
    req = PODSubmissionRequest(
        receiver_name="Far Driver",
        submitted_latitude=18.5204,
        submitted_longitude=73.8567
    )

    res = pod_service.submit_proof_of_delivery(UUID(str(stop.id)), req)

    assert res.is_geofence_verified is False
    assert res.geo_distance_offset_meters > 100000.0  # > 100 km
