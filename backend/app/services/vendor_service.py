"""
Vendor service layer containing business logic.
"""
from typing import List, Tuple, Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorUpdate
from app.repositories.vendor_repository import VendorRepository
from app.utils.exceptions import NotFoundError, DuplicateEntryError, BusinessLogicError
from app.models.user import User


class VendorService:
    """Service for vendor business logic."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = VendorRepository(db)

    def get_vendor(self, vendor_id: UUID) -> Vendor:
        """
        Get vendor by ID.

        Raises:
            NotFoundError: If vendor not found
        """
        vendor = self.repository.get_by_id(vendor_id)
        if not vendor:
            raise NotFoundError(f"Vendor with ID {vendor_id} not found")
        return vendor

    def get_vendors(
        self,
        page: int = 1,
        page_size: int = 20,
        is_active: Optional[bool] = None,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Vendor], int]:
        """Get paginated vendors with filters."""
        skip = (page - 1) * page_size
        return self.repository.get_all(
            skip=skip,
            limit=page_size,
            is_active=is_active,
            category=category,
            search=search
        )

    def create_vendor(self, data: VendorCreate, current_user: Optional[User] = None) -> Vendor:
        """
        Create a new vendor.

        Business Rules:
        - Vendor code must be unique
        """
        if self.repository.exists_by_code(data.vendor_code):
            raise DuplicateEntryError(f"Vendor with code '{data.vendor_code}' already exists")

        return self.repository.create(data)

    def update_vendor(self, vendor_id: UUID, data: VendorUpdate, current_user: Optional[User] = None) -> Vendor:
        """
        Update an existing vendor.

        Business Rules:
        - Cannot change vendor code to existing one
        """
        vendor = self.get_vendor(vendor_id)

        if data.vendor_code and data.vendor_code != vendor.vendor_code:
            if self.repository.exists_by_code(data.vendor_code, exclude_id=vendor_id):
                raise DuplicateEntryError(f"Vendor with code '{data.vendor_code}' already exists")

        return self.repository.update(vendor, data)

    def delete_vendor(self, vendor_id: UUID, current_user: Optional[User] = None) -> None:
        """Delete a vendor record."""
        vendor = self.get_vendor(vendor_id)
        self.repository.delete(vendor)

    def get_vendor_scorecard(self, vendor_id: UUID) -> dict:
        """
        Get vendor scorecard metrics.

        Aggregates purchase orders, total spend, and linked contracts.
        """
        vendor = self.get_vendor(vendor_id)

        # Count purchase orders & calculate spend
        from app.models.inventory import PurchaseOrder
        po_query = self.db.query(
            func.count(PurchaseOrder.id).label('count'),
            func.coalesce(func.sum(PurchaseOrder.cost), 0.0).label('spend')
        ).filter(
            (PurchaseOrder.vendor_id == vendor_id) | (PurchaseOrder.vendor_name == vendor.name)
        ).first()

        po_count = po_query.count if po_query is not None else 0
        total_spend = Decimal(str(po_query.spend if po_query is not None else 0.0))

        # Count linked active documents/contracts
        from app.models.document import Document
        contracts_count = self.db.query(Document).filter(
            Document.vendor_id == vendor_id,
            Document.status == 'Active'
        ).count()

        return {
            "vendor": vendor,
            "purchase_orders_count": po_count,
            "total_spend": total_spend,
            "active_contracts_count": contracts_count
        }
