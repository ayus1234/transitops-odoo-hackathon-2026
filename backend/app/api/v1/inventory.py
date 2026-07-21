from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Any
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_active_user, RoleChecker
from app.models.user import User

from app.schemas.inventory import (
    InventoryItemCreate, 
    InventoryItemUpdate, 
    InventoryItemResponse, 
    InventoryDashboardSummary,
    InventoryHistoryResponse,
    InventoryAdjustmentRequest
)
from app.services.inventory_service import InventoryService
from app.schemas.common import SuccessResponse, PaginatedResponse, PaginationMeta

router = APIRouter()

@router.get("/dashboard", response_model=SuccessResponse)
def get_inventory_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    service = InventoryService(db)
    summary = service.get_dashboard_summary()
    return SuccessResponse(success=True, message="Success", data=summary.model_dump())

@router.get("/summary", response_model=SuccessResponse)
def get_inventory_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    # Similar to dashboard, kept for API completeness as per requirements
    service = InventoryService(db)
    summary = service.get_dashboard_summary()
    return SuccessResponse(success=True, message="Success", data=summary.model_dump())

@router.get("/parts", response_model=PaginatedResponse[InventoryItemResponse])
def get_inventory_parts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = None,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    service = InventoryService(db)
    skip = (page - 1) * page_size
    items, total = service.repository.get_all(skip=skip, limit=page_size, status=status, search=search)
    return PaginatedResponse(
        success=True,
        data=[InventoryItemResponse.model_validate(i) for i in items],
        pagination=PaginationMeta(total_items=total, page=page, page_size=page_size, total_pages=(total + page_size - 1) // page_size)
    )

@router.get("/search", response_model=SuccessResponse)
def search_inventory(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    service = InventoryService(db)
    items, total = service.repository.get_all(skip=0, limit=50, search=query)
    return SuccessResponse(
        success=True,
        message="Search results",
        data=[InventoryItemResponse.model_validate(i).model_dump() for i in items]
    )

@router.get("/filter", response_model=SuccessResponse)
def filter_inventory(
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    service = InventoryService(db)
    items, total = service.repository.get_all(skip=0, limit=100, status=status)
    return SuccessResponse(
        success=True,
        message="Filtered results",
        data=[InventoryItemResponse.model_validate(i).model_dump() for i in items]
    )

@router.get("/history", response_model=PaginatedResponse[InventoryHistoryResponse])
def get_inventory_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    part_id: UUID = None,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    service = InventoryService(db)
    skip = (page - 1) * page_size
    logs, total = service.history_repo.get_all(skip=skip, limit=page_size, part_id=part_id, search=search)
    return PaginatedResponse(
        success=True,
        data=[InventoryHistoryResponse.model_validate(l) for l in logs],
        pagination=PaginationMeta(total_items=total, page=page, page_size=page_size, total_pages=(total + page_size - 1) // page_size)
    )

@router.get("/history/search", response_model=SuccessResponse)
def search_inventory_history(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    service = InventoryService(db)
    logs, total = service.history_repo.get_all(skip=0, limit=50, search=query)
    return SuccessResponse(
        success=True,
        message="History search results",
        data=[InventoryHistoryResponse.model_validate(l).model_dump() for l in logs]
    )

@router.get("/history/filter", response_model=SuccessResponse)
def filter_inventory_history(
    part_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    service = InventoryService(db)
    logs, total = service.history_repo.get_all(skip=0, limit=100, part_id=part_id)
    return SuccessResponse(
        success=True,
        message="History filter results",
        data=[InventoryHistoryResponse.model_validate(l).model_dump() for l in logs]
    )

@router.post("/{part_id}/adjust", response_model=SuccessResponse)
def adjust_inventory_stock(
    part_id: UUID,
    request: InventoryAdjustmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["Super Admin", "Administrator", "Fleet Manager", "Maintenance Manager"]))
) -> Any:
    service = InventoryService(db)
    item = service.update_stock(
        part_id=part_id,
        quantity_change=request.quantity_change,
        type=request.type,
        user_id=current_user.id,
        reference_id=request.reference_id,
        vendor=request.vendor,
        cost=request.cost
    )
    return SuccessResponse(
        success=True,
        message=f"Stock successfully adjusted by {request.quantity_change}",
        data=InventoryItemResponse.model_validate(item).model_dump()
    )
