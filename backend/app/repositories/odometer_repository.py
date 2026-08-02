"""
Odometer reading repository for database operations.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.models.odometer_reading import OdometerReading


class OdometerRepository:
    """Repository for odometer reading database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, reading: OdometerReading) -> OdometerReading:
        """Insert a new odometer reading."""
        self.db.add(reading)
        self.db.commit()
        self.db.refresh(reading)
        return reading

    def get_by_id(self, reading_id: UUID) -> Optional[OdometerReading]:
        """Get a single reading by ID."""
        return self.db.query(OdometerReading).filter(
            OdometerReading.id == reading_id
        ).first()

    def get_latest_for_vehicle(self, vehicle_id: UUID) -> Optional[OdometerReading]:
        """Get the most recent reading for a vehicle."""
        return (
            self.db.query(OdometerReading)
            .filter(OdometerReading.vehicle_id == vehicle_id)
            .order_by(desc(OdometerReading.recorded_at))
            .first()
        )

    def get_history(
        self,
        vehicle_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[OdometerReading], int]:
        """
        Get paginated odometer history for a vehicle, newest first.

        Returns:
            Tuple of (readings list, total count)
        """
        query = self.db.query(OdometerReading).filter(
            OdometerReading.vehicle_id == vehicle_id
        )

        total = query.count()
        readings = (
            query
            .order_by(desc(OdometerReading.recorded_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return readings, total

    def get_stats(self, vehicle_id: UUID) -> dict:
        """Get aggregate statistics for a vehicle's odometer readings."""
        result = self.db.query(
            func.count(OdometerReading.id).label('total_readings'),
            func.min(OdometerReading.reading_km).label('first_reading_km'),
            func.max(OdometerReading.reading_km).label('last_reading_km'),
            func.min(OdometerReading.recorded_at).label('first_reading_date'),
            func.max(OdometerReading.recorded_at).label('last_reading_date'),
        ).filter(
            OdometerReading.vehicle_id == vehicle_id
        ).first()

        return {
            'total_readings': result.total_readings or 0,
            'first_reading_km': result.first_reading_km,
            'last_reading_km': result.last_reading_km,
            'first_reading_date': result.first_reading_date,
            'last_reading_date': result.last_reading_date,
        }
