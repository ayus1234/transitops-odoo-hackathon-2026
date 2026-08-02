"""
Dispatch Service — Pre-validation and Operational Dispatch Control Center.
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.job import Job
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.trip import Trip
from app.models.document import Document
from app.repositories.job_repository import JobRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.driver_repository import DriverRepository
from app.repositories.trip_repository import TripRepository
from app.services.trip_service import TripService
from app.schemas.trip import TripCreate, TripDispatch
from app.utils.exceptions import BusinessLogicError, NotFoundError


class DispatchService:
    """Operational dispatch board engine."""

    def __init__(self, db: Session):
        self.db = db
        self.job_repo = JobRepository(db)
        self.vehicle_repo = VehicleRepository(db)
        self.driver_repo = DriverRepository(db)
        self.trip_repo = TripRepository(db)
        self.trip_service = TripService(db)

    def get_dispatch_board_data(self) -> Dict[str, Any]:
        """Fetch all operational control center queues and KPIs."""
        # 1. Unassigned jobs (Pending & no trip)
        unassigned_jobs = self.db.query(Job).filter(
            Job.status == "Pending",
            Job.trip_id.is_(None)
        ).order_by(Job.priority.desc(), Job.created_at.asc()).all()

        # 2. Available vehicles (Available status & not in maintenance)
        available_vehicles = self.db.query(Vehicle).filter(
            Vehicle.status == "Available"
        ).order_by(Vehicle.capacity_kg.desc()).all()

        # 3. Available drivers (Available status)
        available_drivers = self.db.query(Driver).filter(
            Driver.status == "Available"
        ).all()

        # 4. Active trips (Dispatched or In Transit)
        active_trips = self.db.query(Trip).filter(
            Trip.status.in_(["Dispatched", "In Transit", "Scheduled"])
        ).order_by(Trip.created_at.desc()).all()

        # 5. Calculate KPIs
        now = datetime.now()
        kpis = {
          "unassigned_jobs_count": len(unassigned_jobs),
          "available_vehicles_count": len(available_vehicles),
          "available_drivers_count": len(available_drivers),
          "active_trips_count": len(active_trips),
          "delayed_trips_count": sum(1 for t in active_trips if getattr(t, 'planned_arrival', None) is not None and getattr(t, 'planned_arrival') < now)
        }

        return {
          "kpis": kpis,
          "unassigned_jobs": unassigned_jobs,
          "available_vehicles": available_vehicles,
          "available_drivers": available_drivers,
          "active_trips": active_trips
        }

    def validate_dispatch(
        self,
        job_id: UUID,
        vehicle_id: UUID,
        driver_id: UUID
    ) -> Dict[str, Any]:
        """Dry-run validation checks before operational dispatch."""
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundError(f"Job {job_id} not found")

        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise NotFoundError(f"Vehicle {vehicle_id} not found")

        driver = self.driver_repo.get_by_id(driver_id)
        if not driver:
            raise NotFoundError(f"Driver {driver_id} not found")

        warnings: List[str] = []
        errors: List[str] = []

        # Check vehicle status
        if vehicle.status not in ["Available", "Acquired"]:
            errors.append(f"Vehicle {vehicle.registration_number} is in '{vehicle.status}' state (must be Available).")

        # Check driver status
        if driver.status != "Available":
            errors.append(f"Driver {driver.license_number} is in '{driver.status}' state (must be Available).")

        # Check capacity
        cargo_weight = float(str(job.cargo_weight_kg)) if job.cargo_weight_kg is not None else 0.0
        vehicle_capacity = float(str(vehicle.capacity_kg)) if vehicle.capacity_kg is not None else 0.0

        if cargo_weight > 0 and vehicle_capacity > 0:
            if cargo_weight > vehicle_capacity:
                errors.append(
                    f"Cargo weight ({cargo_weight} kg) exceeds vehicle capacity ({vehicle_capacity} kg)."
                )

        # Check license validity
        if driver.license_expiry_date and driver.license_expiry_date < datetime.now().date():
            errors.append(f"Driver license {driver.license_number} expired on {driver.license_expiry_date}.")

        # Check medical fitness validity if present
        if getattr(driver, 'medical_fitness_expiry', None) is not None:
            if getattr(driver, 'medical_fitness_expiry') < datetime.now().date():
                warnings.append(f"Driver medical fitness expired on {driver.medical_fitness_expiry}.")

        utilization_pct = round((cargo_weight / vehicle_capacity) * 100, 1) if vehicle_capacity > 0 else 0.0

        return {
          "valid": len(errors) == 0,
          "errors": errors,
          "warnings": warnings,
          "cargo_weight_kg": cargo_weight,
          "vehicle_capacity_kg": vehicle_capacity,
          "utilization_pct": utilization_pct
        }

    def assign_and_dispatch(
        self,
        job_id: UUID,
        vehicle_id: UUID,
        driver_id: UUID,
        notes: Optional[str] = None
    ) -> Trip:
        """Atomically create trip, link job, update statuses, and dispatch."""
        # 1. Pre-validation
        val = self.validate_dispatch(job_id, vehicle_id, driver_id)
        if not val["valid"]:
            raise BusinessLogicError(
                f"Dispatch validation failed: {'; '.join(val['errors'])}",
                code="BIZ_DISPATCH_001"
            )

        job = self.job_repo.get_by_id(job_id)
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        driver = self.driver_repo.get_by_id(driver_id)

        if job is None or vehicle is None or driver is None:
            raise NotFoundError("Job, vehicle, or driver not found")

        # 2. Create Trip
        now = datetime.now()
        cargo_weight = Decimal(str(job.cargo_weight_kg)) if job.cargo_weight_kg is not None else Decimal("100.0")

        trip_data = TripCreate(
            vehicle_id=UUID(str(vehicle.id)),
            driver_id=UUID(str(driver.id)),
            source=str(job.pickup_address),
            destination=str(job.delivery_address),
            cargo_weight_kg=cargo_weight,
            planned_distance_km=Decimal("150.0"),
            planned_departure=now,
            planned_arrival=now + timedelta(hours=4),
            notes=notes or f"Dispatched for Customer Job {job.job_number} ({job.customer_name})"
        )

        trip = self.trip_service.create_trip(trip_data)

        # 3. Update Job
        setattr(job, 'trip_id', trip.id)
        setattr(job, 'status', 'Assigned')

        # 4. Immediately dispatch trip
        start_odo = float(str(vehicle.current_odometer_km)) if vehicle.current_odometer_km is not None else 0.0
        dispatched_trip = self.trip_service.dispatch_trip(UUID(str(trip.id)), TripDispatch(start_odometer_km=Decimal(str(start_odo))))
        setattr(job, 'status', 'In Transit')

        self.db.commit()
        self.db.refresh(job)
        self.db.refresh(dispatched_trip)

        return dispatched_trip

