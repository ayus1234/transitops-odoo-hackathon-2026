"""
Trip service layer containing business logic.
"""
from datetime import datetime
from typing import List, Tuple, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.schemas.trip import TripCreate, TripUpdate, TripDispatch, TripComplete, TripCancel
from app.repositories.trip_repository import TripRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.driver_repository import DriverRepository
from app.utils.exceptions import (
    NotFoundError,
    BusinessLogicError,
    ValidationError
)


class TripService:
    """Service for trip business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = TripRepository(db)
        self.vehicle_repository = VehicleRepository(db)
        self.driver_repository = DriverRepository(db)
    
    def get_trip(self, trip_id: UUID) -> Trip:
        """
        Get trip by ID.
        
        Raises:
            NotFoundError: If trip not found
        """
        trip = self.repository.get_by_id(trip_id)
        if not trip:
            raise NotFoundError(f"Trip with ID {trip_id} not found")
        return trip
    
    def get_trips(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        vehicle_id: UUID | None = None,
        driver_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        search: str | None = None
    ) -> Tuple[List[Trip], int]:
        """
        Get all trips with pagination and filters.
        
        Returns:
            Tuple of (trips list, total count)
        """
        skip = (page - 1) * page_size
        return self.repository.get_all(
            skip=skip,
            limit=page_size,
            status=status,
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            start_date=start_date,
            end_date=end_date,
            search=search
        )
    
    def create_trip(self, trip_data: TripCreate, created_by: UUID | None = None) -> Trip:
        """
        Create a new trip.
        
        Business Rules:
        - Vehicle must exist
        - Driver must exist
        - Vehicle must be available (status = 'Available')
        - Driver must be available (status = 'Available')
        - Driver's license must not be expired
        - Cargo weight cannot exceed vehicle capacity
        - Vehicle must not be assigned to another active trip
        - Driver must not be assigned to another active trip
        - Planned arrival must be after planned departure
        
        Raises:
            NotFoundError: If vehicle or driver not found
            BusinessLogicError: If business rules are violated
        """
        # 1. Validate vehicle exists
        vehicle = self.vehicle_repository.get_by_id(trip_data.vehicle_id)
        if not vehicle:
            raise NotFoundError(f"Vehicle with ID {trip_data.vehicle_id} not found")
        
        # 2. Validate driver exists
        driver = self.driver_repository.get_by_id(trip_data.driver_id)
        if not driver:
            raise NotFoundError(f"Driver with ID {trip_data.driver_id} not found")
        
        # 3. Validate vehicle is available
        if not vehicle.is_available:
            raise BusinessLogicError(
                f"Vehicle '{vehicle.registration_number}' is not available. "
                f"Current status: '{vehicle.status}'",
                code="BIZ_002"
            )
        
        # 4. Validate driver is available
        if not driver.is_available:
            raise BusinessLogicError(
                f"Driver with license '{driver.license_number}' is not available. "
                f"Current status: '{driver.status}'",
                code="BIZ_003"
            )
        
        # 5. Validate driver's license is not expired
        if not driver.is_license_valid:
            raise BusinessLogicError(
                f"Driver's license '{driver.license_number}' has expired on "
                f"{driver.license_expiry_date}. Cannot assign to trip.",
                code="BIZ_004"
            )
        
        # 6. Validate cargo weight does not exceed vehicle capacity
        if float(trip_data.cargo_weight_kg) > float(vehicle.capacity_kg):
            raise BusinessLogicError(
                f"Cargo weight ({trip_data.cargo_weight_kg} kg) exceeds vehicle capacity "
                f"({vehicle.capacity_kg} kg) for vehicle '{vehicle.registration_number}'",
                code="BIZ_005"
            )
        
        # 7. Validate vehicle is not assigned to another active trip
        active_vehicle_trip = self.repository.get_active_trip_by_vehicle(trip_data.vehicle_id)
        if active_vehicle_trip:
            raise BusinessLogicError(
                f"Vehicle '{vehicle.registration_number}' is already assigned to "
                f"trip '{active_vehicle_trip.trip_number}' (status: {active_vehicle_trip.status})",
                code="BIZ_006"
            )
        
        # 8. Validate driver is not assigned to another active trip
        active_driver_trip = self.repository.get_active_trip_by_driver(trip_data.driver_id)
        if active_driver_trip:
            raise BusinessLogicError(
                f"Driver with license '{driver.license_number}' is already assigned to "
                f"trip '{active_driver_trip.trip_number}' (status: {active_driver_trip.status})",
                code="BIZ_007"
            )
        
        # Generate trip number
        trip_number = self.repository.get_next_trip_number()
        
        # Build trip data dict
        trip_dict = trip_data.model_dump()
        trip_dict["trip_number"] = trip_number
        trip_dict["status"] = "Draft"
        if created_by:
            trip_dict["created_by"] = created_by
        
        return self.repository.create(trip_dict)
    
    def update_trip(self, trip_id: UUID, trip_data: TripUpdate) -> Trip:
        """
        Update an existing trip.
        
        Business Rules:
        - Can only update trips in Draft status
        - If vehicle_id changes, new vehicle must exist and be available
        - If driver_id changes, new driver must exist and be available
        - Cargo weight cannot exceed vehicle capacity
        
        Raises:
            NotFoundError: If trip, vehicle, or driver not found
            BusinessLogicError: If business rules are violated
        """
        trip = self.get_trip(trip_id)
        
        # Can only update Draft trips
        if not trip.is_draft:
            raise BusinessLogicError(
                f"Cannot update trip '{trip.trip_number}' with status '{trip.status}'. "
                "Only Draft trips can be updated.",
                code="BIZ_008"
            )
        
        update_data = trip_data.model_dump(exclude_unset=True)
        
        # If vehicle_id is being changed, validate new vehicle
        if "vehicle_id" in update_data:
            new_vehicle = self.vehicle_repository.get_by_id(update_data["vehicle_id"])
            if not new_vehicle:
                raise NotFoundError(f"Vehicle with ID {update_data['vehicle_id']} not found")
            if not new_vehicle.is_available:
                raise BusinessLogicError(
                    f"Vehicle '{new_vehicle.registration_number}' is not available. "
                    f"Current status: '{new_vehicle.status}'",
                    code="BIZ_002"
                )
            # Check for active trip on new vehicle (excluding current trip)
            active_trip = self.repository.get_active_trip_by_vehicle(update_data["vehicle_id"])
            if active_trip and active_trip.id != trip_id:
                raise BusinessLogicError(
                    f"Vehicle '{new_vehicle.registration_number}' is already assigned to "
                    f"trip '{active_trip.trip_number}'",
                    code="BIZ_006"
                )
        
        # If driver_id is being changed, validate new driver
        if "driver_id" in update_data:
            new_driver = self.driver_repository.get_by_id(update_data["driver_id"])
            if not new_driver:
                raise NotFoundError(f"Driver with ID {update_data['driver_id']} not found")
            if not new_driver.is_available:
                raise BusinessLogicError(
                    f"Driver with license '{new_driver.license_number}' is not available. "
                    f"Current status: '{new_driver.status}'",
                    code="BIZ_003"
                )
            if not new_driver.is_license_valid:
                raise BusinessLogicError(
                    f"Driver's license '{new_driver.license_number}' has expired.",
                    code="BIZ_004"
                )
            # Check for active trip on new driver (excluding current trip)
            active_trip = self.repository.get_active_trip_by_driver(update_data["driver_id"])
            if active_trip and active_trip.id != trip_id:
                raise BusinessLogicError(
                    f"Driver is already assigned to trip '{active_trip.trip_number}'",
                    code="BIZ_007"
                )
        
        # Validate cargo weight if being updated
        if "cargo_weight_kg" in update_data:
            vehicle_id = update_data.get("vehicle_id", trip.vehicle_id)
            vehicle = self.vehicle_repository.get_by_id(vehicle_id)
            if float(update_data["cargo_weight_kg"]) > float(vehicle.capacity_kg):
                raise BusinessLogicError(
                    f"Cargo weight ({update_data['cargo_weight_kg']} kg) exceeds vehicle capacity "
                    f"({vehicle.capacity_kg} kg)",
                    code="BIZ_005"
                )
        
        return self.repository.update(trip, update_data)
    
    def dispatch_trip(self, trip_id: UUID, dispatch_data: TripDispatch) -> Trip:
        """
        Dispatch a trip.
        
        Business Rules:
        - Trip must be in Draft status
        - Vehicle must still be Available
        - Driver must still be Available
        - Sets vehicle status to 'On Trip'
        - Sets driver status to 'On Trip'
        - Sets trip status to 'Dispatched'
        
        Raises:
            NotFoundError: If trip not found
            BusinessLogicError: If business rules are violated
        """
        trip = self.get_trip(trip_id)
        
        if not trip.can_be_dispatched:
            raise BusinessLogicError(
                f"Cannot dispatch trip '{trip.trip_number}' with status '{trip.status}'. "
                "Only Draft trips can be dispatched.",
                code="BIZ_009"
            )
        
        # Re-validate vehicle availability
        vehicle = self.vehicle_repository.get_by_id(trip.vehicle_id)
        if not vehicle.is_available:
            raise BusinessLogicError(
                f"Vehicle '{vehicle.registration_number}' is no longer available. "
                f"Current status: '{vehicle.status}'",
                code="BIZ_002"
            )
        
        # Re-validate driver availability
        driver = self.driver_repository.get_by_id(trip.driver_id)
        if not driver.is_available:
            raise BusinessLogicError(
                f"Driver with license '{driver.license_number}' is no longer available. "
                f"Current status: '{driver.status}'",
                code="BIZ_003"
            )
        
        # Re-validate driver license
        if not driver.is_license_valid:
            raise BusinessLogicError(
                f"Driver's license '{driver.license_number}' has expired.",
                code="BIZ_004"
            )
        
        # Update vehicle status to 'On Trip'
        vehicle.status = 'On Trip'
        
        # Update driver status to 'On Trip'
        driver.status = 'On Trip'
        
        # Update trip
        update_data = {
            "status": "Dispatched",
            "start_odometer_km": float(dispatch_data.start_odometer_km),
            "actual_departure": datetime.utcnow()
        }
        
        return self.repository.update(trip, update_data)
    
    def complete_trip(self, trip_id: UUID, complete_data: TripComplete) -> Trip:
        """
        Complete a trip.
        
        Business Rules:
        - Trip must be in Dispatched status
        - End odometer must be >= start odometer
        - Sets vehicle status to 'Available'
        - Sets driver status to 'Available'
        - Increments driver total_trips
        - Updates vehicle odometer
        
        Raises:
            NotFoundError: If trip not found
            BusinessLogicError: If business rules are violated
        """
        trip = self.get_trip(trip_id)
        
        if not trip.can_be_completed:
            raise BusinessLogicError(
                f"Cannot complete trip '{trip.trip_number}' with status '{trip.status}'. "
                "Only Dispatched trips can be completed.",
                code="BIZ_010"
            )
        
        # Validate end odometer
        if trip.start_odometer_km is not None:
            if float(complete_data.end_odometer_km) < float(trip.start_odometer_km):
                raise BusinessLogicError(
                    f"End odometer ({complete_data.end_odometer_km} km) cannot be less than "
                    f"start odometer ({trip.start_odometer_km} km)",
                    code="BIZ_011"
                )
        
        # Get vehicle and driver
        vehicle = self.vehicle_repository.get_by_id(trip.vehicle_id)
        driver = self.driver_repository.get_by_id(trip.driver_id)
        
        # Restore vehicle status and update odometer
        vehicle.status = 'Available'
        vehicle.current_odometer_km = float(complete_data.end_odometer_km)
        
        # Restore driver status and increment total trips
        driver.status = 'Available'
        driver.total_trips = driver.total_trips + 1
        
        # Update trip
        update_data = {
            "status": "Completed",
            "end_odometer_km": float(complete_data.end_odometer_km),
            "actual_distance_km": float(complete_data.actual_distance_km),
            "actual_arrival": datetime.utcnow()
        }
        
        if complete_data.fuel_consumed_liters is not None:
            update_data["fuel_consumed_liters"] = float(complete_data.fuel_consumed_liters)
        
        if complete_data.notes is not None:
            update_data["notes"] = complete_data.notes
        
        return self.repository.update(trip, update_data)
    
    def cancel_trip(self, trip_id: UUID, cancel_data: TripCancel) -> Trip:
        """
        Cancel a trip.
        
        Business Rules:
        - Trip must be in Draft or Dispatched status
        - If Dispatched: restore vehicle and driver to 'Available'
        
        Raises:
            NotFoundError: If trip not found
            BusinessLogicError: If business rules are violated
        """
        trip = self.get_trip(trip_id)
        
        if not trip.can_be_cancelled:
            raise BusinessLogicError(
                f"Cannot cancel trip '{trip.trip_number}' with status '{trip.status}'. "
                "Only Draft or Dispatched trips can be cancelled.",
                code="BIZ_012"
            )
        
        # If trip was Dispatched, restore vehicle and driver status
        if trip.is_active:
            vehicle = self.vehicle_repository.get_by_id(trip.vehicle_id)
            driver = self.driver_repository.get_by_id(trip.driver_id)
            
            if vehicle.status == 'On Trip':
                vehicle.status = 'Available'
            
            if driver.status == 'On Trip':
                driver.status = 'Available'
        
        # Update trip
        update_data = {
            "status": "Cancelled",
            "notes": f"Cancelled: {cancel_data.reason}" + (
                f"\n\nPrevious notes: {trip.notes}" if trip.notes else ""
            )
        }
        
        return self.repository.update(trip, update_data)
    
    def delete_trip(self, trip_id: UUID) -> None:
        """
        Delete a trip.
        
        Business Rules:
        - Cannot delete Dispatched trips (must cancel first)
        - Cannot delete Completed trips
        
        Raises:
            NotFoundError: If trip not found
            BusinessLogicError: If business rules are violated
        """
        trip = self.get_trip(trip_id)
        
        if trip.status in ['Dispatched']:
            raise BusinessLogicError(
                f"Cannot delete trip '{trip.trip_number}' with status '{trip.status}'. "
                "Cancel the trip first.",
                code="BIZ_013"
            )
        
        if trip.status == 'Completed':
            raise BusinessLogicError(
                f"Cannot delete completed trip '{trip.trip_number}'. "
                "Completed trips must be retained for records.",
                code="BIZ_014"
            )
        
        self.repository.delete(trip)
    
    def get_trip_statistics(self) -> dict:
        """Get trip statistics by status."""
        return self.repository.count_by_status()
