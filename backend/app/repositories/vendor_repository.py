"""
Vendor repository for database operations.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import or_, desc
from sqlalchemy.orm import Session

from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorUpdate


class VendorRepository:
    """Repository for vendor database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, vendor_id: UUID) -> Optional[Vendor]:
        """Get vendor by ID."""
        return self.db.query(Vendor).filter(Vendor.id == vendor_id).first()

    def get_by_code(self, vendor_code: str) -> Optional[Vendor]:
        """Get vendor by unique vendor code."""
        return self.db.query(Vendor).filter(Vendor.vendor_code == vendor_code).first()

    def create(self, vendor_data: VendorCreate) -> Vendor:
        """Create a new vendor."""
        vendor = Vendor(**vendor_data.model_dump())
        self.db.add(vendor)
        self.db.commit()
        self.db.refresh(vendor)
        return vendor

    def update(self, vendor: Vendor, update_data: VendorUpdate) -> Vendor:
        """Update an existing vendor."""
        data = update_data.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(vendor, field, value)

        self.db.commit()
        self.db.refresh(vendor)
        return vendor

    def delete(self, vendor: Vendor) -> None:
        """Delete a vendor record."""
        self.db.delete(vendor)
        self.db.commit()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[Vendor], int]:
        """Get paginated vendors with optional filtering."""
        query = self.db.query(Vendor)

        if is_active is not None:
            query = query.filter(Vendor.is_active == is_active)

        if search:
            search_filter = or_(
                Vendor.name.ilike(f"%{search}%"),
                Vendor.vendor_code.ilike(f"%{search}%"),
                Vendor.contact_person.ilike(f"%{search}%"),
                Vendor.email.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        total = query.count()
        vendors = query.order_by(desc(Vendor.created_at)).offset(skip).limit(limit).all()

        # In-memory category filter if category requested (JSON array)
        if category:
            vendors = [v for v in vendors if v.categories and category in v.categories]

        return vendors, total

    def exists_by_code(self, vendor_code: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if vendor code already exists."""
        query = self.db.query(Vendor).filter(Vendor.vendor_code == vendor_code)
        if exclude_id:
            query = query.filter(Vendor.id != exclude_id)
        return query.first() is not None
