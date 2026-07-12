"""
Driver service layer containing business logic.
"""
from typing import List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import date

from app.models.driver import Driver
from app.models.user import User
from app.models.role import Role
from app.schemas.driver import DriverCreate, DriverUpdate
from app.repositories.driver_repository import DriverRepository
from app.core.security import get_password_hash
from app.utils.exceptions import (
    NotFoundError,
    DuplicateEntryError,
    BusinessLogicError,
    ValidationError
)


class DriverService:
    """Service for driver business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = DriverRepository(db)
    
    def get_driver(self, driver_id: UUID) -> Driver:
        """
        Get driver by ID.
        
        Raises:
            NotFoundError: If driver not found
        """
        driver = self.repository.get_by_id(driver_id)
        if not driver:
            raise NotFoundError(f"Driver with ID {driver_id} not found")
        return driver
    
    def get_drivers(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        search: str | None = None,
        license_expiring_soon: bool = False
    ) -> Tuple[List[Driver], int]:
        """
        Get all drivers with pagination and filters.
        
        Returns:
            Tuple of (drivers list, total count)
        """
        skip = (page - 1) * page_size
        return self.repository.get_all(
            skip=skip,
            limit=page_size,
            status=status,
            search=search,
            license_expiring_soon=license_expiring_soon
        )
    
    def create_driver(self, driver_data: DriverCreate) -> Driver:
        """
        Create a new driver with user account.
        
        Business Rules:
        - License number must be unique
        - User email must be unique
        - Driver must be at least 18 years old
        - License must not be expired
        - License expiry date must be after issue date
        
        Raises:
            DuplicateEntryError: If license number or email already exists
            ValidationError: If business rules violated
        """
        # Check if license number already exists
        if self.repository.exists_by_license(driver_data.license_number):
            raise DuplicateEntryError(
                f"Driver with license number '{driver_data.license_number}' already exists"
            )
        
        # Validate license dates
        if driver_data.license_expiry_date <= driver_data.license_issue_date:
            raise ValidationError("License expiry date must be after issue date")
        
        # Validate license is not expired
        if driver_data.license_expiry_date < date.today():
            raise ValidationError("Cannot create driver with expired license")
        
        # Validate age (at least 18 years old)
        age = self._calculate_age(driver_data.date_of_birth)
        if age < 18:
            raise ValidationError("Driver must be at least 18 years old")
        
        # Check if user email already exists
        user_data = driver_data.user
        existing_user = self.db.query(User).filter(User.email == user_data['email']).first()
        if existing_user:
            raise DuplicateEntryError(f"User with email '{user_data['email']}' already exists")
        
        # Get Driver role
        driver_role = self.db.query(Role).filter(Role.name == "Driver").first()
        if not driver_role:
            raise NotFoundError("Driver role not found in system")
        
        # Create user account
        user = User(
            email=user_data['email'],
            password_hash=get_password_hash(user_data['password']),
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone_number=user_data.get('phone_number'),
            role_id=driver_role.id,
            is_active=True
        )
        self.db.add(user)
        self.db.flush()  # Get user.id without committing
        
        # Create driver record
        driver_dict = driver_data.model_dump(exclude={'user'})
        driver_dict['user_id'] = user.id
        
        driver = self.repository.create(driver_dict)
        return driver
    
    def update_driver(self, driver_id: UUID, driver_data: DriverUpdate) -> Driver:
        """
        Update an existing driver.
        
        Business Rules:
        - Cannot change license to existing one
        - Cannot manually set status to 'On Trip' (only through trip dispatch)
        - Cannot change status while 'On Trip'
        - License dates must be valid
        
        Raises:
            NotFoundError: If driver not found
            DuplicateEntryError: If new license number already exists
            BusinessLogicError: If business rule violated
        """
        driver = self.get_driver(driver_id)
        
        # Check license number uniqueness if being updated
        if (driver_data.license_number and
            driver_data.license_number != driver.license_number):
            if self.repository.exists_by_license(
                driver_data.license_number,
                exclude_id=driver_id
            ):
                raise DuplicateEntryError(
                    f"Driver with license number '{driver_data.license_number}' already exists"
                )
        
        # Validate license dates if both are provided
        issue_date = driver_data.license_issue_date or driver.license_issue_date
        expiry_date = driver_data.license_expiry_date or driver.license_expiry_date
        
        if expiry_date <= issue_date:
            raise ValidationError("License expiry date must be after issue date")
        
        # Validate status change
        if driver_data.status and driver_data.status != driver.status:
            self._validate_status_change(driver, driver_data.status)
        
        return self.repository.update(driver, driver_data)
    
    def delete_driver(self, driver_id: UUID) -> None:
        """
        Delete a driver.
        
        Business Rules:
        - Cannot delete driver that is On Trip
        - Cannot delete driver with active trips (would need to check trips table)
        
        Raises:
            NotFoundError: If driver not found
            BusinessLogicError: If driver is in use
        """
        driver = self.get_driver(driver_id)
        
        # Check if driver can be deleted
        if driver.status == 'On Trip':
            raise BusinessLogicError(
                f"Cannot delete driver that is 'On Trip'. "
                "Complete or cancel the active trip first.",
                code="BIZ_002"
            )
        
        # Delete associated user account
        if driver.user:
            self.db.delete(driver.user)
        
        self.repository.delete(driver)
    
    def get_available_drivers(self) -> List[Driver]:
        """Get all drivers available for assignment with valid licenses."""
        return self.repository.get_available_drivers()
    
    def get_drivers_with_expiring_licenses(self, days: int = 30) -> List[Driver]:
        """Get drivers whose licenses are expiring within specified days."""
        return self.repository.get_drivers_with_expiring_licenses(days)
    
    def get_driver_statistics(self) -> dict:
        """Get driver statistics by status."""
        return self.repository.count_by_status()
    
    def _calculate_age(self, birth_date: date) -> int:
        """Calculate age from birth date."""
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    
    def _validate_status_change(self, driver: Driver, new_status: str) -> None:
        """
        Validate status change business rules.
        
        Rules:
        - Manual status changes to 'On Trip' are not allowed
        - Cannot change from 'On Trip' directly (must complete trip first)
        - Can change to 'Available' from 'Off Duty' or 'Suspended'
        - Can change to 'Off Duty' or 'Suspended' from 'Available'
        """
        current_status = driver.status
        
        # Cannot manually set to 'On Trip'
        if new_status == 'On Trip':
            raise BusinessLogicError(
                "Cannot manually set driver status to 'On Trip'. "
                "Use trip dispatch to assign driver.",
                code="BIZ_007"
            )
        
        # Cannot change from 'On Trip' directly
        if current_status == 'On Trip':
            raise BusinessLogicError(
                f"Cannot change status from 'On Trip' to '{new_status}'. "
                "Complete or cancel the trip first.",
                code="BIZ_002"
            )
