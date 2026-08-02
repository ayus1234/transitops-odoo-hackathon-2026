"""
Odometer service layer containing business logic.
Enforces anti-regression rule and syncs Vehicle.current_odometer_km.
"""
from datetime import datetime, timezone
from typing import List, Tuple, Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.odometer_reading import OdometerReading
from app.models.vehicle import Vehicle
from app.schemas.odometer import OdometerReadingCreate
from app.repositories.odometer_repository import OdometerRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.utils.exceptions import NotFoundError, BusinessLogicError
from app.models.user import User


class OdometerService:
    """Service for odometer reading business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = OdometerRepository(db)
        self.vehicle_repo = VehicleRepository(db)

    def record_reading(
        self,
        vehicle_id: UUID,
        data: OdometerReadingCreate,
        current_user: Optional[User] = None
    ) -> OdometerReading:
        """
        Record a new odometer reading.

        Business Rules:
        - New reading must be ≥ previous reading (anti-regression)
        - Unless source is 'correction' (authorised override)
        - Updates Vehicle.current_odometer_km to match

        Raises:
            NotFoundError: If vehicle not found
            BusinessLogicError: If reading regresses without correction source
        """
        # Verify vehicle exists
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise NotFoundError(f"Vehicle with ID {vehicle_id} not found")

        # Anti-regression check
        latest = self.repo.get_latest_for_vehicle(vehicle_id)
        if latest and data.source != 'correction':
            if data.reading_km < latest.reading_km:
                raise BusinessLogicError(
                    f"Odometer reading {data.reading_km} km is less than "
                    f"the previous reading of {latest.reading_km} km. "
                    f"Use source='correction' to authorise a rollback.",
                    code="BIZ_ODO_001"
                )

        # Create reading
        reading = OdometerReading(
            vehicle_id=vehicle_id,
            reading_km=data.reading_km,
            recorded_at=data.recorded_at or datetime.now(timezone.utc),
            source=data.source,
            recorded_by=current_user.id if current_user else None,
            trip_id=data.trip_id,
            notes=data.notes,
        )
        self.repo.create(reading)

        # Sync vehicle's current odometer
        vehicle.current_odometer_km = data.reading_km
        self.db.commit()
        self.db.refresh(vehicle)

        return reading

    def get_history(
        self,
        vehicle_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[OdometerReading], int]:
        """
        Get paginated odometer history for a vehicle.

        Raises:
            NotFoundError: If vehicle not found
        """
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise NotFoundError(f"Vehicle with ID {vehicle_id} not found")

        skip = (page - 1) * page_size
        return self.repo.get_history(vehicle_id, skip=skip, limit=page_size)

    def get_stats(self, vehicle_id: UUID) -> dict:
        """
        Get odometer statistics for a vehicle.

        Returns dict with total_readings, first/last reading, total distance.

        Raises:
            NotFoundError: If vehicle not found
        """
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise NotFoundError(f"Vehicle with ID {vehicle_id} not found")

        stats = self.repo.get_stats(vehicle_id)
        stats['vehicle_id'] = vehicle_id
        stats['current_odometer_km'] = vehicle.current_odometer_km

        # Calculate total distance
        if stats['first_reading_km'] is not None and stats['last_reading_km'] is not None:
            stats['total_distance_km'] = Decimal(str(stats['last_reading_km'])) - Decimal(str(stats['first_reading_km']))
        else:
            stats['total_distance_km'] = None

        return stats
