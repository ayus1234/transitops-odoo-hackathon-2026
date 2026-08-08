"""
Unit tests for Priority 4 — Event-Driven Audit Trail Engine.
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
from app.schemas.job import JobCreate
from app.schemas.vehicle import VehicleCreate
from app.schemas.pod import PODSubmissionRequest
from app.services.job_service import JobService
from app.services.vehicle_service import VehicleService
from app.services.dispatch_service import DispatchService
from app.services.pod_service import PODService
from app.services.audit_event_service import AuditEventService


def test_end_to_end_job_lifecycle_audit_timeline(db_session):
    job_service = JobService(db_session)
    vehicle_service = VehicleService(db_session)
    dispatch_service = DispatchService(db_session)
    pod_service = PODService(db_session)
    audit_service = AuditEventService(db_session)

    role = db_session.query(Role).first()
    if not role:
        role = Role(name="Driver", permissions={})
        db_session.add(role)
        db_session.commit()

    ts = int(datetime.now().timestamp() * 1000)

    # 1. Create Job (Triggers JOB_CREATED)
    job = job_service.create_job(JobCreate(
        customer_name=f"Audit Test Corp {ts}",
        pickup_address="Bhiwandi Hub",
        delivery_address="JNPT Port",
        cargo_weight_kg=12000.00
    ))

    # 2. Create Vehicle & Driver
    vehicle = vehicle_service.create_vehicle(VehicleCreate(
        registration_number=f"AUD-{ts}",
        vehicle_name="Audit Heavy Truck",
        vehicle_type="Truck",
        capacity_kg=25000.00,
        fuel_type="Diesel",
        status="Available"
    ))

    user = User(
        email=f"audit.driver.{ts}@transitops.com",
        password_hash="hash",
        first_name="Audit",
        last_name="Driver",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    driver = Driver(
        user_id=user.id,
        license_number=f"LIC-AUD-{ts}",
        license_category="Heavy Commercial",
        license_issue_date=date(2020, 1, 1),
        date_of_birth=date(1990, 1, 1),
        status="Available",
        license_expiry_date=date(2035, 1, 1)
    )
    db_session.add(driver)
    db_session.commit()

    # 3. Assign & Dispatch (Triggers JOB_ASSIGNED, TRIP_CREATED, TRIP_STARTED)
    dispatched_trip = dispatch_service.assign_and_dispatch(
        job_id=UUID(str(job.id)),
        vehicle_id=UUID(str(vehicle.id)),
        driver_id=UUID(str(driver.id)),
        notes="Audit stream dispatch test"
    )

    # Add Delivery TripStop linked to Job
    stop = TripStop(
        trip_id=dispatched_trip.id,
        sequence=1,
        location_name="JNPT Port Gate 4",
        latitude=Decimal("18.9500"),
        longitude=Decimal("72.9500"),
        stop_type="Delivery",
        job_id=job.id,
        status="Pending"
    )
    db_session.add(stop)
    db_session.commit()

    # 4. Submit Proof of Delivery (Triggers POD_RECEIVED, STOP_COMPLETED, DELIVERED)
    pod_req = PODSubmissionRequest(
        receiver_name="Port Authority Manager",
        submitted_latitude=18.9501,
        submitted_longitude=72.9501,
        notes="Cargo verified and cleared"
    )
    pod_service.submit_proof_of_delivery(UUID(str(stop.id)), pod_req)

    # 5. Query Audit Event Timeline for Job
    timeline = audit_service.get_job_timeline(UUID(str(job.id)))

    assert timeline.entity_id == UUID(str(job.id))
    assert timeline.total_events >= 6

    event_types = [e.event_type for e in timeline.events]

    assert "JOB_CREATED" in event_types
    assert "JOB_ASSIGNED" in event_types
    assert "TRIP_CREATED" in event_types
    assert "TRIP_STARTED" in event_types
    assert "POD_RECEIVED" in event_types
    assert "DELIVERED" in event_types

    # Verify chronological ordering
    job_created_event = next(e for e in timeline.events if e.event_type == "JOB_CREATED")
    delivered_event = next(e for e in timeline.events if e.event_type == "DELIVERED")

    assert job_created_event.created_at <= delivered_event.created_at
    assert delivered_event.payload is not None
    assert delivered_event.payload.get("receiver_name") == "Port Authority Manager"
