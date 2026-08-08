"""
Unit tests for Feature 2.2 — Operational Dispatch Board.
"""
import pytest
from datetime import datetime, date, timedelta
from uuid import UUID

from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.job import Job
from app.schemas.job import JobCreate
from app.schemas.vehicle import VehicleCreate
from app.services.dispatch_service import DispatchService
from app.services.job_service import JobService
from app.services.vehicle_service import VehicleService
from app.utils.exceptions import BusinessLogicError


def test_get_dispatch_board_queues_and_kpis(db_session):
    dispatch_service = DispatchService(db_session)

    # Fetch initial board
    board = dispatch_service.get_dispatch_board_data()

    assert "kpis" in board
    assert "unassigned_jobs" in board
    assert "available_vehicles" in board
    assert "available_drivers" in board
    assert "active_trips" in board
    assert isinstance(board["kpis"]["unassigned_jobs_count"], int)


from app.models.user import User
from app.models.role import Role

def test_validate_dispatch_success_and_overweight_warning(db_session):
    job_service = JobService(db_session)
    vehicle_service = VehicleService(db_session)
    dispatch_service = DispatchService(db_session)

    # Fetch role
    role = db_session.query(Role).first()
    if not role:
        role = Role(name="Driver", permissions={})
        db_session.add(role)
        db_session.commit()

    # 1. Create Heavy Job
    job = job_service.create_job(JobCreate(
        customer_name="Heavy Heavy Metals",
        pickup_address="Bhiwandi",
        delivery_address="JNPT",
        cargo_weight_kg=35000.00
    ))

    # 2. Create Small Vehicle (10,000 kg capacity)
    reg_num = f"VAL-{int(datetime.now().timestamp())}"
    vehicle = vehicle_service.create_vehicle(VehicleCreate(
        registration_number=reg_num,
        vehicle_name="Small Delivery Van",
        vehicle_type="Truck",
        capacity_kg=10000.00,
        fuel_type="Diesel",
        status="Available"
    ))

    # 3. Create User & Driver
    user = User(
        email=f"driver.val.{int(datetime.now().timestamp())}@transitops.com",
        password_hash="hash",
        first_name="Val",
        last_name="Driver",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    driver = Driver(
        user_id=user.id,
        license_number=f"LIC-{int(datetime.now().timestamp())}",
        license_category="Heavy Vehicle",
        license_issue_date=date(2020, 1, 1),
        date_of_birth=date(1990, 1, 1),
        status="Available",
        license_expiry_date=date(2035, 1, 1)
    )
    db_session.add(driver)
    db_session.commit()
    db_session.refresh(driver)

    from uuid import UUID

    # Validate dry-run
    val = dispatch_service.validate_dispatch(
        job_id=UUID(str(job.id)),
        vehicle_id=UUID(str(vehicle.id)),
        driver_id=UUID(str(driver.id))
    )

    assert val["valid"] is False
    assert len(val["errors"]) > 0
    assert "exceeds vehicle capacity" in val["errors"][0]


def test_assign_and_dispatch_operational_flow(db_session):
    job_service = JobService(db_session)
    vehicle_service = VehicleService(db_session)
    dispatch_service = DispatchService(db_session)

    # Fetch role
    role = db_session.query(Role).first()
    if not role:
        role = Role(name="Driver", permissions={})
        db_session.add(role)
        db_session.commit()

    # 1. Create Valid Job
    job = job_service.create_job(JobCreate(
        customer_name="Express Logistics",
        pickup_address="Delhi Warehouse",
        delivery_address="Jaipur Depot",
        cargo_weight_kg=8000.00
    ))

    # 2. Create Suitable Available Vehicle (20,000 kg capacity)
    reg_num = f"DISP-{int(datetime.now().timestamp())}"
    vehicle = vehicle_service.create_vehicle(VehicleCreate(
        registration_number=reg_num,
        vehicle_name="Heavy Freight Truck",
        vehicle_type="Truck",
        capacity_kg=20000.00,
        fuel_type="Diesel",
        status="Available"
    ))

    # 3. Create User & Available Driver
    user = User(
        email=f"driver.disp.{int(datetime.now().timestamp())}@transitops.com",
        password_hash="hash",
        first_name="Disp",
        last_name="Driver",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    driver = Driver(
        user_id=user.id,
        license_number=f"LIC-DISP-{int(datetime.now().timestamp())}",
        license_category="Heavy Vehicle",
        license_issue_date=date(2020, 1, 1),
        date_of_birth=date(1990, 1, 1),
        status="Available",
        license_expiry_date=date(2035, 1, 1)
    )
    db_session.add(driver)
    db_session.commit()
    db_session.refresh(driver)

    # Assign & Dispatch
    dispatched_trip = dispatch_service.assign_and_dispatch(
        job_id=UUID(str(job.id)),
        vehicle_id=UUID(str(vehicle.id)),
        driver_id=UUID(str(driver.id)),
        notes="Urgent dispatch by control tower"
    )

    assert dispatched_trip.id is not None
    assert dispatched_trip.status in ["Dispatched", "In Transit"]

    # Verify updated statuses
    db_session.refresh(job)
    db_session.refresh(vehicle)
    db_session.refresh(driver)

    assert job.status == "In Transit"
    assert vehicle.status in ["On Trip", "Active"]
    assert driver.status == "On Trip"


def test_dispatch_conflict_when_already_assigned(db_session):
    job_service = JobService(db_session)
    vehicle_service = VehicleService(db_session)
    dispatch_service = DispatchService(db_session)

    role = db_session.query(Role).first()
    if not role:
        role = Role(name="Driver", permissions={})
        db_session.add(role)
        db_session.commit()

    # 1. Create Job
    job = job_service.create_job(JobCreate(
        customer_name="Conflict Corp",
        pickup_address="Bandra",
        delivery_address="Andheri",
        cargo_weight_kg=5000.00
    ))

    # 2. Create Vehicle
    reg_num = f"CONF-{int(datetime.now().timestamp())}"
    vehicle = vehicle_service.create_vehicle(VehicleCreate(
        registration_number=reg_num,
        vehicle_name="Conflict Freight",
        vehicle_type="Truck",
        capacity_kg=15000.00,
        fuel_type="Diesel",
        status="Available"
    ))

    # 3. Create Driver
    user = User(
        email=f"driver.conf.{int(datetime.now().timestamp())}@transitops.com",
        password_hash="hash",
        first_name="Conf",
        last_name="Driver",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    driver = Driver(
        user_id=user.id,
        license_number=f"LIC-CONF-{int(datetime.now().timestamp())}",
        license_category="Heavy Vehicle",
        license_issue_date=date(2020, 1, 1),
        date_of_birth=date(1990, 1, 1),
        status="Available",
        license_expiry_date=date(2035, 1, 1)
    )
    db_session.add(driver)
    db_session.commit()

    # Dispatch first time (Succeeds)
    dispatch_service.assign_and_dispatch(
        job_id=UUID(str(job.id)),
        vehicle_id=UUID(str(vehicle.id)),
        driver_id=UUID(str(driver.id))
    )

    # Attempt second dispatch with same job/vehicle/driver (Must fail with BIZ_DISPATCH_CONFLICT)
    with pytest.raises(BusinessLogicError) as exc_info:
        dispatch_service.assign_and_dispatch(
            job_id=UUID(str(job.id)),
            vehicle_id=UUID(str(vehicle.id)),
            driver_id=UUID(str(driver.id))
        )

    assert exc_info.value.code == "BIZ_DISPATCH_CONFLICT"
    assert "no longer pending" in exc_info.value.message or "no longer available" in exc_info.value.message


def test_dispatch_transaction_rollback_on_failure(db_session, monkeypatch):
    job_service = JobService(db_session)
    vehicle_service = VehicleService(db_session)
    dispatch_service = DispatchService(db_session)

    role = db_session.query(Role).first()
    if not role:
        role = Role(name="Driver", permissions={})
        db_session.add(role)
        db_session.commit()

    # 1. Create Job
    job = job_service.create_job(JobCreate(
        customer_name="Rollback Test Inc",
        pickup_address="Pune",
        delivery_address="Mumbai",
        cargo_weight_kg=4000.00
    ))

    # 2. Create Vehicle
    reg_num = f"ROLL-{int(datetime.now().timestamp())}"
    vehicle = vehicle_service.create_vehicle(VehicleCreate(
        registration_number=reg_num,
        vehicle_name="Rollback Express",
        vehicle_type="Truck",
        capacity_kg=12000.00,
        fuel_type="Diesel",
        status="Available"
    ))

    # 3. Create Driver
    user = User(
        email=f"driver.roll.{int(datetime.now().timestamp())}@transitops.com",
        password_hash="hash",
        first_name="Roll",
        last_name="Driver",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    driver = Driver(
        user_id=user.id,
        license_number=f"LIC-ROLL-{int(datetime.now().timestamp())}",
        license_category="Heavy Vehicle",
        license_issue_date=date(2020, 1, 1),
        date_of_birth=date(1990, 1, 1),
        status="Available",
        license_expiry_date=date(2035, 1, 1)
    )
    db_session.add(driver)
    db_session.commit()

    # Mock trip_service.dispatch_trip to raise an unhandled error midway
    def mock_dispatch_fail(*args, **kwargs):
        raise RuntimeError("Simulated mid-flight network/database failure")

    monkeypatch.setattr(dispatch_service.trip_service, "dispatch_trip", mock_dispatch_fail)

    # Execute assign_and_dispatch — must raise BusinessLogicError and rollback
    with pytest.raises(BusinessLogicError) as exc_info:
        dispatch_service.assign_and_dispatch(
            job_id=UUID(str(job.id)),
            vehicle_id=UUID(str(vehicle.id)),
            driver_id=UUID(str(driver.id))
        )

    assert exc_info.value.code == "BIZ_DISPATCH_FAIL"
    assert "rolled back safely" in exc_info.value.message

    # Verify rollback: vehicle remains Available, driver remains Available, job remains Pending
    db_session.rollback()  # Refresh session view
    refreshed_job = db_session.query(Job).filter(Job.id == job.id).first()
    refreshed_vehicle = db_session.query(Vehicle).filter(Vehicle.id == vehicle.id).first()
    refreshed_driver = db_session.query(Driver).filter(Driver.id == driver.id).first()

    assert refreshed_job.status == "Pending"
    assert refreshed_job.trip_id is None
    assert refreshed_vehicle.status == "Available"
    assert refreshed_driver.status == "Available"
