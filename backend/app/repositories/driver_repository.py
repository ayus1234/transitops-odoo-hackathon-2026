"""
Driver repository for database operations.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import Session
from datetime import date

from app.models.driver import Driver
from app.models.user import User
from app.schemas.driver import DriverCreate, DriverUpdate


class DriverRepository:
    """Repository for driver database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, driver_id: UUID) -> Optional[Driver]:
        """Get driver by ID."""
        return self.db.query(Driver).filter(Driver.id == driver_id).first()
    
    def get_by_user_id(self, user_id: UUID) -> Optional[Driver]:
        """Get driver by user ID."""
        return self.db.query(Driver).filter(Driver.user_id == user_id).first()
    
    def get_by_license(self, license_number: str) -> Optional[Driver]:
        """Get driver by license number."""
        return self.db.query(Driver).filter(
            Driver.license_number == license_number
        ).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
        license_expiring_soon: bool = False
    ) -> tuple[List[Driver], int]:
        """
        Get all drivers with optional filters.
        
        Returns:
            Tuple of (drivers list, total count)
        """
        query = self.db.query(Driver)
        
        # Apply filters
        if status:
            query = query.filter(Driver.status == status)
        
        if search:
            # Join with user for name search
            query = query.join(User, Driver.user_id == User.id)
            search_filter = or_(
                Driver.license_number.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if license_expiring_soon:
            # Get drivers whose license expires within 30 days
            from datetime import timedelta
            expiry_threshold = date.today() + timedelta(days=30)
            query = query.filter(
                and_(
                    Driver.license_expiry_date <= expiry_threshold,
                    Driver.license_expiry_date >= date.today()
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        drivers = query.order_by(Driver.created_at.desc()).offset(skip).limit(limit).all()
        
        return drivers, total
    
    def create(self, driver_data: dict) -> Driver:
        """Create a new driver."""
        driver = Driver(**driver_data)
        self.db.add(driver)
        self.db.commit()
        self.db.refresh(driver)
        return driver
    
    def update(self, driver: Driver, driver_data: DriverUpdate) -> Driver:
        """Update an existing driver."""
        update_data = driver_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(driver, field, value)
        
        self.db.commit()
        self.db.refresh(driver)
        return driver
    
    def delete(self, driver: Driver) -> None:
        """Delete a driver."""
        self.db.delete(driver)
        self.db.commit()
    
    def count_by_status(self) -> dict:
        """Get count of drivers by status."""
        result = self.db.query(
            Driver.status,
            func.count(Driver.id).label('count')
        ).group_by(Driver.status).all()
        
        return {status: count for status, count in result}
    
    def get_available_drivers(self) -> List[Driver]:
        """Get all available drivers with valid licenses."""
        today = date.today()
        return self.db.query(Driver).filter(
            and_(
                Driver.status == 'Available',
                Driver.license_expiry_date > today
            )
        ).all()
    
    def get_drivers_with_expiring_licenses(self, days: int = 30) -> List[Driver]:
        """Get drivers whose licenses are expiring within specified days."""
        from datetime import timedelta
        today = date.today()
        expiry_threshold = today + timedelta(days=days)
        
        return self.db.query(Driver).filter(
            and_(
                Driver.license_expiry_date <= expiry_threshold,
                Driver.license_expiry_date >= today
            )
        ).all()
    
    def exists_by_license(self, license_number: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if driver exists by license number."""
        query = self.db.query(Driver).filter(
            Driver.license_number == license_number
        )
        
        if exclude_id:
            query = query.filter(Driver.id != exclude_id)
        
        return query.first() is not None
    
    def exists_by_user_id(self, user_id: UUID, exclude_id: Optional[UUID] = None) -> bool:
        """Check if driver exists for user."""
        query = self.db.query(Driver).filter(
            Driver.user_id == user_id
        )
        
        if exclude_id:
            query = query.filter(Driver.id != exclude_id)
        
        return query.first() is not None
