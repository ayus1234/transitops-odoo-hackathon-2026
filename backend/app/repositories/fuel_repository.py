"""
Fuel repository for database operations.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import or_, and_, text
from sqlalchemy.orm import Session

from app.models.fuel import Fuel


class FuelRepository:
    """Repository for fuel database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, fuel_id: UUID) -> Optional[Fuel]:
        """Get fuel record by ID."""
        return self.db.query(Fuel).filter(
            Fuel.id == fuel_id
        ).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        vehicle_id: Optional[UUID] = None,
        trip_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search: Optional[str] = None
    ) -> tuple[List[Fuel], int]:
        """
        Get all fuel records with optional filters.

        Returns:
            Tuple of (fuel list, total count)
        """
        query = self.db.query(Fuel)

        # Apply filters
        if vehicle_id:
            query = query.filter(Fuel.vehicle_id == vehicle_id)
            
        if trip_id:
            query = query.filter(Fuel.trip_id == trip_id)

        if start_date:
            query = query.filter(Fuel.refuel_date >= start_date)

        if end_date:
            query = query.filter(Fuel.refuel_date <= end_date)

        if search:
            search_filter = or_(
                Fuel.station_name.ilike(f"%{search}%"),
                Fuel.location.ilike(f"%{search}%"),
                Fuel.receipt_number.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        records = query.order_by(
            Fuel.refuel_date.desc()
        ).offset(skip).limit(limit).all()

        return records, total

    def create(self, fuel_data: dict) -> Fuel:
        """Create a new fuel record."""
        fuel = Fuel(**fuel_data)
        self.db.add(fuel)
        self.db.commit()
        self.db.refresh(fuel)
        return fuel

    def update(self, fuel: Fuel, update_data: dict) -> Fuel:
        """Update an existing fuel record."""
        for field, value in update_data.items():
            setattr(fuel, field, value)

        self.db.commit()
        self.db.refresh(fuel)
        return fuel

    def delete(self, fuel: Fuel) -> None:
        """Delete a fuel record."""
        self.db.delete(fuel)
        self.db.commit()
