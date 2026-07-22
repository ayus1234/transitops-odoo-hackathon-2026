"""
Vehicle repository for database operations.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class VehicleRepository:
    """Repository for vehicle database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, vehicle_id: UUID) -> Optional[Vehicle]:
        """Get vehicle by ID."""
        return self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    def get_by_registration(self, registration_number: str) -> Optional[Vehicle]:
        """Get vehicle by registration number."""
        return self.db.query(Vehicle).filter(
            Vehicle.registration_number == registration_number
        ).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        vehicle_type: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[Vehicle], int]:
        """
        Get all vehicles with optional filters.
        
        Returns:
            Tuple of (vehicles list, total count)
        """
        query = self.db.query(Vehicle)
        
        # Apply filters
        if status:
            query = query.filter(Vehicle.status == status)
        
        if vehicle_type:
            query = query.filter(Vehicle.vehicle_type == vehicle_type)
        
        if search:
            search_filter = or_(
                Vehicle.registration_number.ilike(f"%{search}%"),
                Vehicle.vehicle_name.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        vehicles = query.order_by(Vehicle.created_at.desc()).offset(skip).limit(limit).all()
        
        return vehicles, total
    
    def create(self, vehicle_data: VehicleCreate) -> Vehicle:
        """Create a new vehicle."""
        vehicle = Vehicle(**vehicle_data.model_dump())
        self.db.add(vehicle)
        self.db.commit()
        self.db.refresh(vehicle)
        return vehicle
    
    def update(self, vehicle: Vehicle, vehicle_data: VehicleUpdate) -> Vehicle:
        """Update an existing vehicle."""
        update_data = vehicle_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(vehicle, field, value)
        
        self.db.commit()
        self.db.refresh(vehicle)
        return vehicle
    
    def delete(self, vehicle: Vehicle) -> None:
        """Delete a vehicle."""
        self.db.delete(vehicle)
        self.db.commit()
    
    def count_by_status(self) -> dict:
        """Get count of vehicles by status."""
        result = self.db.query(
            Vehicle.status,
            func.count(Vehicle.id).label('count')
        ).group_by(Vehicle.status).all()
        
        return {status: count for status, count in result}
    
    def get_available_vehicles(self) -> List[Vehicle]:
        """Get all available vehicles."""
        return self.db.query(Vehicle).filter(Vehicle.status == 'Available').all()
    
    def exists_by_registration(self, registration_number: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if vehicle exists by registration number."""
        query = self.db.query(Vehicle).filter(
            Vehicle.registration_number == registration_number
        )
        
        if exclude_id:
            query = query.filter(Vehicle.id != exclude_id)
        
        return query.first() is not None
