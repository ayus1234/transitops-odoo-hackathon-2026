"""
Trip repository for database operations.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import Session

from app.models.trip import Trip


class TripRepository:
    """Repository for trip database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, trip_id: UUID) -> Optional[Trip]:
        """Get trip by ID."""
        return self.db.query(Trip).filter(Trip.id == trip_id).first()
    
    def get_by_trip_number(self, trip_number: str) -> Optional[Trip]:
        """Get trip by trip number."""
        return self.db.query(Trip).filter(
            Trip.trip_number == trip_number
        ).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        vehicle_id: Optional[UUID] = None,
        driver_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        search: Optional[str] = None
    ) -> tuple[List[Trip], int]:
        """
        Get all trips with optional filters.
        
        Returns:
            Tuple of (trips list, total count)
        """
        query = self.db.query(Trip)
        
        # Apply filters
        if status:
            query = query.filter(Trip.status == status)
        
        if vehicle_id:
            query = query.filter(Trip.vehicle_id == vehicle_id)
        
        if driver_id:
            query = query.filter(Trip.driver_id == driver_id)
        
        if start_date:
            query = query.filter(Trip.planned_departure >= start_date)
        
        if end_date:
            query = query.filter(Trip.planned_departure <= end_date)
        
        if search:
            search_filter = or_(
                Trip.trip_number.ilike(f"%{search}%"),
                Trip.source.ilike(f"%{search}%"),
                Trip.destination.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        trips = query.order_by(Trip.created_at.desc()).offset(skip).limit(limit).all()
        
        return trips, total
    
    def create(self, trip_data: dict) -> Trip:
        """Create a new trip."""
        trip = Trip(**trip_data)
        self.db.add(trip)
        self.db.commit()
        self.db.refresh(trip)
        return trip
    
    def update(self, trip: Trip, update_data: dict) -> Trip:
        """Update an existing trip."""
        for field, value in update_data.items():
            setattr(trip, field, value)
        
        self.db.commit()
        self.db.refresh(trip)
        return trip
    
    def delete(self, trip: Trip) -> None:
        """Delete a trip."""
        self.db.delete(trip)
        self.db.commit()
    
    def count_by_status(self) -> dict:
        """Get count of trips by status."""
        result = self.db.query(
            Trip.status,
            func.count(Trip.id).label('count')
        ).group_by(Trip.status).all()
        
        return {status: count for status, count in result}
    
    def get_active_trip_by_vehicle(self, vehicle_id: UUID) -> Optional[Trip]:
        """Get active trip for a vehicle (Draft or Dispatched)."""
        return self.db.query(Trip).filter(
            and_(
                Trip.vehicle_id == vehicle_id,
                Trip.status.in_(['Draft', 'Dispatched'])
            )
        ).first()
    
    def get_active_trip_by_driver(self, driver_id: UUID) -> Optional[Trip]:
        """Get active trip for a driver (Draft or Dispatched)."""
        return self.db.query(Trip).filter(
            and_(
                Trip.driver_id == driver_id,
                Trip.status.in_(['Draft', 'Dispatched'])
            )
        ).first()
    
    def get_next_trip_number(self) -> str:
        """Generate next trip number (TRP-YYYY-NNNNN)."""
        from datetime import date
        year = date.today().year
        prefix = f"TRP-{year}-"
        
        # Get the last trip number for this year
        last_trip = self.db.query(Trip).filter(
            Trip.trip_number.like(f"{prefix}%")
        ).order_by(Trip.trip_number.desc()).first()
        
        if last_trip:
            # Extract sequence number and increment
            last_seq = int(last_trip.trip_number.replace(prefix, ""))
            next_seq = last_seq + 1
        else:
            next_seq = 1
        
        return f"{prefix}{next_seq:05d}"
    
    def get_trips_by_vehicle(
        self,
        vehicle_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> tuple[List[Trip], int]:
        """Get trips for a specific vehicle."""
        query = self.db.query(Trip).filter(Trip.vehicle_id == vehicle_id)
        
        if status:
            query = query.filter(Trip.status == status)
        
        total = query.count()
        trips = query.order_by(Trip.created_at.desc()).offset(skip).limit(limit).all()
        
        return trips, total
    
    def get_trips_by_driver(
        self,
        driver_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> tuple[List[Trip], int]:
        """Get trips for a specific driver."""
        query = self.db.query(Trip).filter(Trip.driver_id == driver_id)
        
        if status:
            query = query.filter(Trip.status == status)
        
        total = query.count()
        trips = query.order_by(Trip.created_at.desc()).offset(skip).limit(limit).all()
        
        return trips, total
