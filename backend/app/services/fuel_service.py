"""
Fuel service layer containing business logic.
"""
from datetime import datetime, timezone
from typing import List, Tuple, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.fuel import Fuel
from app.schemas.fuel import FuelCreate, FuelUpdate, FuelEfficiencyStats
from app.repositories.fuel_repository import FuelRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.trip_repository import TripRepository
from app.utils.exceptions import (
    NotFoundError,
    BusinessLogicError,
)
from app.services.activity_service import activity_service
from app.schemas.activity import ActivityCreate
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.models.user import User


class FuelService:
    """Service for fuel business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = FuelRepository(db)
        self.vehicle_repository = VehicleRepository(db)
        self.trip_repository = TripRepository(db)

    # ============================================================
    # READ
    # ============================================================

    def get_fuel_entry(self, fuel_id: UUID) -> Fuel:
        """
        Get fuel record by ID.

        Raises:
            NotFoundError: If record not found
        """
        record = self.repository.get_by_id(fuel_id)
        if not record:
            raise NotFoundError(
                f"Fuel record with ID {fuel_id} not found"
            )
        return record

    def get_fuel_entries(
        self,
        page: int = 1,
        page_size: int = 20,
        vehicle_id: UUID | None = None,
        trip_id: UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        search: str | None = None
    ) -> Tuple[List[Fuel], int]:
        """
        Get all fuel records with pagination and filters.

        Returns:
            Tuple of (records list, total count)
        """
        skip = (page - 1) * page_size
        return self.repository.get_all(
            skip=skip,
            limit=page_size,
            vehicle_id=vehicle_id,
            trip_id=trip_id,
            start_date=start_date,
            end_date=end_date,
            search=search
        )

    # ============================================================
    # CREATE
    # ============================================================

    def create_fuel_entry(
        self,
        data: FuelCreate,
        recorded_by: UUID | None = None
    ) -> Fuel:
        """
        Create a new fuel record.

        Business Rules:
        - Vehicle must exist and not be Retired
        - Fuel type must match vehicle's fuel type
        - Trip must exist (if provided)
        - Refuel date cannot be in the future
        - Odometer reading must be >= vehicle's current odometer
        - Total cost is auto-calculated

        Raises:
            NotFoundError: If vehicle or trip not found
            BusinessLogicError: If business rules violated
        """
        # 1. Validate vehicle exists
        vehicle = self.vehicle_repository.get_by_id(data.vehicle_id)
        if not vehicle:
            raise NotFoundError(
                f"Vehicle with ID {data.vehicle_id} not found"
            )

        # 2. Validate vehicle is not retired
        if not vehicle.is_operational:
            raise BusinessLogicError(
                f"Vehicle '{vehicle.registration_number}' is retired "
                "and cannot be refueled.",
                code="BIZ_030"
            )

        # 3. Validate fuel type matches vehicle
        if data.fuel_type != vehicle.fuel_type:
            raise BusinessLogicError(
                f"Fuel type mismatch. Vehicle '{vehicle.registration_number}' "
                f"uses '{vehicle.fuel_type}', but '{data.fuel_type}' was provided.",
                code="BIZ_031"
            )

        # 4. Validate trip if provided
        if data.trip_id:
            trip = self.trip_repository.get_by_id(data.trip_id)
            if not trip:
                raise NotFoundError(f"Trip with ID {data.trip_id} not found")
            if trip.vehicle_id != data.vehicle_id:
                raise BusinessLogicError(
                    f"Trip '{trip.trip_number}' belongs to a different vehicle.",
                    code="BIZ_032"
                )

        # 5. Validate refuel date is not in future
        refuel_date = data.refuel_date or datetime.now(timezone.utc)
        if refuel_date > datetime.now(timezone.utc):
            raise BusinessLogicError(
                "Refuel date cannot be in the future.",
                code="BIZ_033"
            )

        # 6. Validate odometer reading
        if vehicle.current_odometer_km and data.odometer_reading < vehicle.current_odometer_km:
            raise BusinessLogicError(
                f"Odometer reading ({data.odometer_reading}) cannot be less than "
                f"vehicle's current odometer ({vehicle.current_odometer_km}).",
                code="BIZ_034"
            )

        # Build data dict
        record_dict = data.model_dump()
        record_dict["refuel_date"] = refuel_date
        
        # Calculate total cost
        record_dict["total_cost"] = float(data.quantity_liters) * float(data.cost_per_liter)
        
        if recorded_by:
            record_dict["recorded_by"] = recorded_by

        record = self.repository.create(record_dict)
        
        if recorded_by:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.FUEL,
                activity_type=ActivityTypeEnum.CREATED,
                title="Fuel Log Added",
                description=f"Refueled vehicle {vehicle.registration_number} with {data.quantity_liters}L.",
                severity=SeverityEnum.SUCCESS,
                status="Success",
                user_id=recorded_by,
                vehicle_id=vehicle.id,
                trip_id=data.trip_id
            ))
            
        return record

    # ============================================================
    # UPDATE
    # ============================================================

    def update_fuel_entry(
        self,
        fuel_id: UUID,
        data: FuelUpdate,
        current_user: User = None
    ) -> Fuel:
        """
        Update a fuel record.

        Business Rules:
        - Re-validates vehicle and trip associations if changed
        - Re-validates fuel type match if changed
        - Recalculates total cost if quantity or price changed
        """
        record = self.get_fuel_entry(fuel_id)
        update_data = data.model_dump(exclude_unset=True)

        # Re-validate vehicle if changed
        if "vehicle_id" in update_data and update_data["vehicle_id"] != record.vehicle_id:
            vehicle = self.vehicle_repository.get_by_id(update_data["vehicle_id"])
            if not vehicle:
                raise NotFoundError(f"Vehicle with ID {update_data['vehicle_id']} not found")
            if not vehicle.is_operational:
                raise BusinessLogicError("Cannot reassign fuel log to a retired vehicle.")
            
            # Check fuel type compatibility
            fuel_type = update_data.get("fuel_type", record.fuel_type)
            if fuel_type != vehicle.fuel_type:
                raise BusinessLogicError(
                    f"Fuel type mismatch. Vehicle uses '{vehicle.fuel_type}'.",
                    code="BIZ_031"
                )

        # Re-validate fuel type if changed (and vehicle hasn't)
        elif "fuel_type" in update_data:
            vehicle = self.vehicle_repository.get_by_id(record.vehicle_id)
            if update_data["fuel_type"] != vehicle.fuel_type:
                raise BusinessLogicError(
                    f"Fuel type mismatch. Vehicle uses '{vehicle.fuel_type}'.",
                    code="BIZ_031"
                )

        # Re-validate trip if changed
        if "trip_id" in update_data and update_data["trip_id"] is not None:
            trip = self.trip_repository.get_by_id(update_data["trip_id"])
            if not trip:
                raise NotFoundError(f"Trip with ID {update_data['trip_id']} not found")
            
            veh_id = update_data.get("vehicle_id", record.vehicle_id)
            if trip.vehicle_id != veh_id:
                raise BusinessLogicError(
                    "Trip belongs to a different vehicle.",
                    code="BIZ_032"
                )

        # Recalculate total cost if quantity or price changed
        if "quantity_liters" in update_data or "cost_per_liter" in update_data:
            qty = update_data.get("quantity_liters", record.quantity_liters)
            cost = update_data.get("cost_per_liter", record.cost_per_liter)
            update_data["total_cost"] = float(qty) * float(cost)

        updated_record = self.repository.update(record, update_data)
        
        if current_user:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.FUEL,
                activity_type=ActivityTypeEnum.UPDATED,
                title="Fuel Log Updated",
                description="Fuel record parameters were modified.",
                severity=SeverityEnum.INFO,
                status="Success",
                user_id=current_user.id,
                vehicle_id=updated_record.vehicle_id,
                trip_id=updated_record.trip_id
            ))
            
        return updated_record

    # ============================================================
    # DELETE
    # ============================================================

    def delete_fuel_entry(self, fuel_id: UUID, current_user: User = None) -> None:
        """Delete a fuel record."""
        record = self.get_fuel_entry(fuel_id)
        
        if current_user:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.FUEL,
                activity_type=ActivityTypeEnum.DELETED,
                title="Fuel Log Deleted",
                description="Fuel record was permanently removed.",
                severity=SeverityEnum.WARNING,
                status="Success",
                user_id=current_user.id
            ))
            
        self.repository.delete(record)

    # ============================================================
    # STATISTICS / EFFICIENCY
    # ============================================================

    def get_efficiency_stats(
        self, 
        vehicle_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[dict]:
        """
        Calculate fuel efficiency statistics.
        This uses raw SQL for the complex aggregation required.
        """
        # Basic query to get total fuel and distance per vehicle
        # Note: In a real app this would require careful odometer tracking logic
        # For hackathon purposes, we use simplified aggregation
        query = """
            SELECT 
                v.id as vehicle_id,
                v.registration_number,
                COALESCE(SUM(f.quantity_liters), 0) as total_fuel,
                COALESCE(MAX(f.odometer_reading) - MIN(f.odometer_reading), 0) as total_distance
            FROM vehicles v
            LEFT JOIN fuel_logs f ON v.id = f.vehicle_id
        """
        
        params = {}
        filters = []
        
        if vehicle_id:
            filters.append("v.id = :vehicle_id")
            params['vehicle_id'] = vehicle_id
            
        if start_date:
            filters.append("f.refuel_date >= :start_date")
            params['start_date'] = start_date
            
        if end_date:
            filters.append("f.refuel_date <= :end_date")
            params['end_date'] = end_date
            
        if filters:
            query += " WHERE " + " AND ".join(filters)
            
        query += " GROUP BY v.id, v.registration_number HAVING SUM(f.quantity_liters) > 0"
        
        result = self.db.execute(text(query), params).fetchall()
        
        stats = []
        for row in result:
            total_dist = float(row.total_distance)
            total_fuel = float(row.total_fuel)
            efficiency = total_dist / total_fuel if total_fuel > 0 else 0
            
            stats.append({
                "vehicle_id": row.vehicle_id,
                "registration_number": row.registration_number,
                "total_fuel_consumed": total_fuel,
                "total_distance": total_dist,
                "avg_fuel_efficiency_kmpl": round(efficiency, 2)
            })
            
        return stats
