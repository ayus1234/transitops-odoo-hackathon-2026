from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Any
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_active_user, RoleChecker
from app.models.user import User
from app.models.inventory import ShipmentStatusEnum

from app.schemas.inventory import (
    PurchaseOrderResponse,
    PurchaseOrderSummary
)
from app.services.purchase_order_service import PurchaseOrderService
from app.schemas.common import SuccessResponse, PaginatedResponse, PaginationMeta

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[PurchaseOrderResponse])
def get_purchase_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = None,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    service = PurchaseOrderService(db)
    skip = (page - 1) * page_size
    orders, total = service.repository.get_all(skip=skip, limit=page_size, status=status, search=search)
    return PaginatedResponse(
        success=True,
        data=[PurchaseOrderResponse.model_validate(o) for o in orders],
        pagination=PaginationMeta(total_items=total, page=page, page_size=page_size, total_pages=(total + page_size - 1) // page_size)
    )

@router.get("/summary", response_model=SuccessResponse)
def get_purchase_order_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    service = PurchaseOrderService(db)
    summary = service.get_summary()
    return SuccessResponse(success=True, message="Success", data=summary.model_dump())

@router.get("/search", response_model=SuccessResponse)
def search_purchase_orders(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    service = PurchaseOrderService(db)
    orders, _ = service.repository.get_all(skip=0, limit=50, search=query)
    return SuccessResponse(
        success=True,
        message="Search results",
        data=[PurchaseOrderResponse.model_validate(o).model_dump() for o in orders]
    )

@router.get("/filter", response_model=SuccessResponse)
def filter_purchase_orders(
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    service = PurchaseOrderService(db)
    orders, _ = service.repository.get_all(skip=0, limit=100, status=status)
    return SuccessResponse(
        success=True,
        message="Filter results",
        data=[PurchaseOrderResponse.model_validate(o).model_dump() for o in orders]
    )

@router.post("/{po_id}/update-status", response_model=SuccessResponse)
def update_po_status(
    po_id: UUID,
    status: ShipmentStatusEnum,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["Super Admin", "Administrator", "Fleet Manager", "Maintenance Manager"]))
) -> Any:
    service = PurchaseOrderService(db)
    order = service.update_shipment_status(po_id, status, current_user)
    return SuccessResponse(
        success=True,
        message=f"Purchase order status updated to {status.value}",
        data=PurchaseOrderResponse.model_validate(order).model_dump()
    )

@router.post("/generate/{req_id}", response_model=SuccessResponse)
def generate_po_from_request(
    req_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["Super Admin", "Administrator", "Fleet Manager"]))
) -> Any:
    service = PurchaseOrderService(db)
    order = service.generate_po_from_request(req_id, current_user)
    return SuccessResponse(
        success=True,
        message="Purchase order generated successfully",
        data=PurchaseOrderResponse.model_validate(order).model_dump()
    )
