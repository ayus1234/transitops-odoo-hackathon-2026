"""
Vendor API endpoints.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, PermissionChecker
from app.models.user import User
from app.schemas.vendor import (
    VendorCreate,
    VendorUpdate,
    VendorResponse,
    VendorListResponse,
    VendorScorecardResponse
)
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.services.vendor_service import VendorService


router = APIRouter()


@router.get("", response_model=PaginatedResponse[VendorListResponse])
def list_vendors(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: Optional[bool] = Query(None, description="Filter active/inactive"),
    category: Optional[str] = Query(None, description="Filter by category (Parts, Service, Fuel, etc.)"),
    search: Optional[str] = Query(None, description="Search name, code, contact, email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vendors", "read"))
):
    """
    Get list of vendors with pagination and filters.

    Permissions: vendors:read
    """
    service = VendorService(db)
    vendors, total = service.get_vendors(
        page=page,
        page_size=page_size,
        is_active=is_active,
        category=category,
        search=search
    )

    return PaginatedResponse(
        success=True,
        data=[VendorListResponse.model_validate(v) for v in vendors],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.post("", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def create_vendor(
    data: VendorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vendors", "create"))
):
    """
    Create a new vendor.

    Permissions: vendors:create
    """
    service = VendorService(db)
    vendor = service.create_vendor(data, current_user)
    return VendorResponse.model_validate(vendor)


@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(
    vendor_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vendors", "read"))
):
    """
    Get vendor by ID.

    Permissions: vendors:read
    """
    service = VendorService(db)
    vendor = service.get_vendor(vendor_id)
    return VendorResponse.model_validate(vendor)


@router.get("/{vendor_id}/scorecard", response_model=VendorScorecardResponse)
def get_vendor_scorecard(
    vendor_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vendors", "read"))
):
    """
    Get vendor performance scorecard.

    Permissions: vendors:read
    """
    service = VendorService(db)
    scorecard = service.get_vendor_scorecard(vendor_id)
    return VendorScorecardResponse(
        vendor=VendorResponse.model_validate(scorecard["vendor"]),
        purchase_orders_count=scorecard["purchase_orders_count"],
        total_spend=scorecard["total_spend"],
        active_contracts_count=scorecard["active_contracts_count"]
    )


@router.put("/{vendor_id}", response_model=VendorResponse)
def update_vendor(
    vendor_id: UUID,
    data: VendorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vendors", "update"))
):
    """
    Update vendor details.

    Permissions: vendors:update
    """
    service = VendorService(db)
    vendor = service.update_vendor(vendor_id, data, current_user)
    return VendorResponse.model_validate(vendor)


@router.delete("/{vendor_id}", response_model=SuccessResponse)
def delete_vendor(
    vendor_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("vendors", "delete"))
):
    """
    Delete a vendor.

    Permissions: vendors:delete
    """
    service = VendorService(db)
    service.delete_vendor(vendor_id, current_user)
    return SuccessResponse(
        success=True,
        message="Vendor deleted successfully"
    )
