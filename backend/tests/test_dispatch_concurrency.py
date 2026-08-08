"""
Real multi-threaded concurrent dispatch contention test.

This test uses INDEPENDENT database connections (not shared savepoints)
to verify that PostgreSQL FOR UPDATE row locking prevents double-dispatch
under true simultaneous contention.

Because this test commits real data to the database, it cleans up after itself.
"""
import pytest
import concurrent.futures
from datetime import datetime, date
from uuid import UUID

from app.models.user import User
from app.models.role import Role
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.job import Job
from app.models.trip import Trip
from app.schemas.job import JobCreate
from app.schemas.vehicle import VehicleCreate
from app.services.job_service import JobService
from app.services.vehicle_service import VehicleService
from app.services.dispatch_service import DispatchService
from app.utils.exceptions import BusinessLogicError
from app.core.database import SessionLocal


def test_multithreaded_concurrent_dispatch_contention():
    """
    Spawns 2 threads that simultaneously call assign_and_dispatch on the SAME
    job/vehicle/driver using independent DB connections.
    Exactly 1 must succeed; the other must receive a conflict/failure error.
    """
    # --- Setup: create seed data with a dedicated session ---
    setup_db = SessionLocal()
    try:
        role = setup_db.query(Role).first()
        if not role:
            role = Role(name="Driver", permissions={})
            setup_db.add(role)
            setup_db.commit()

        job_service = JobService(setup_db)
        vehicle_service = VehicleService(setup_db)

        ts = int(datetime.now().timestamp() * 1000)

        job = job_service.create_job(JobCreate(
            customer_name=f"Concurrency Test {ts}",
            pickup_address="Warehouse Alpha",
            delivery_address="Depot Beta",
            cargo_weight_kg=5000.00
        ))

        vehicle = vehicle_service.create_vehicle(VehicleCreate(
            registration_number=f"CONC-{ts}",
            vehicle_name=f"Concurrency Truck {ts}",
            vehicle_type="Truck",
            capacity_kg=18000.00,
            fuel_type="Diesel",
            status="Available"
        ))

        user = User(
            email=f"driver.conc.{ts}@transitops.com",
            password_hash="hash",
            first_name="Concurrency",
            last_name="Driver",
            role_id=role.id,
            is_active=True
        )
        setup_db.add(user)
        setup_db.commit()

        driver = Driver(
            user_id=user.id,
            license_number=f"LIC-CONC-{ts}",
            license_category="Heavy Vehicle",
            license_issue_date=date(2020, 1, 1),
            date_of_birth=date(1990, 1, 1),
            status="Available",
            license_expiry_date=date(2035, 1, 1)
        )
        setup_db.add(driver)
        setup_db.commit()

        job_id = UUID(str(job.id))
        vehicle_id = UUID(str(vehicle.id))
        driver_id = UUID(str(driver.id))
    finally:
        setup_db.close()

    # --- Execute: two threads dispatch simultaneously ---
    def worker_dispatch(worker_id: int):
        thread_db = SessionLocal()
        try:
            ds = DispatchService(thread_db)
            res = ds.assign_and_dispatch(
                job_id, vehicle_id, driver_id,
                notes=f"Dispatched by Thread-{worker_id}"
            )
            return {"status": "SUCCESS", "trip_id": str(res.id), "worker": worker_id}
        except BusinessLogicError as ble:
            return {"status": "CONFLICT", "code": ble.code, "message": ble.message, "worker": worker_id}
        except Exception as ex:
            return {"status": "ERROR", "message": str(ex), "worker": worker_id}
        finally:
            thread_db.close()

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(worker_dispatch, i) for i in range(2)]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    # --- Assert ---
    successes = [r for r in results if r["status"] == "SUCCESS"]
    conflicts = [r for r in results if r["status"] in ("CONFLICT", "ERROR")]

    print(f"THREAD RESULTS: {results}")

    assert len(successes) == 1, f"Expected exactly 1 success, got {len(successes)}: {results}"
    assert len(conflicts) == 1, f"Expected exactly 1 conflict, got {len(conflicts)}: {results}"

    # --- Cleanup: remove test data ---
    cleanup_db = SessionLocal()
    try:
        # Delete trip(s) created by the successful dispatch
        cleanup_db.query(Trip).filter(Trip.vehicle_id == vehicle_id).delete()
        cleanup_db.query(Job).filter(Job.id == job_id).delete()
        cleanup_db.query(Driver).filter(Driver.id == driver_id).delete()
        cleanup_db.query(Vehicle).filter(Vehicle.id == vehicle_id).delete()
        cleanup_db.query(User).filter(User.id == cleanup_db.query(Driver).filter(Driver.id == driver_id).first().user_id if cleanup_db.query(Driver).filter(Driver.id == driver_id).first() else None).delete()
        cleanup_db.commit()
    except Exception:
        cleanup_db.rollback()
    finally:
        cleanup_db.close()
