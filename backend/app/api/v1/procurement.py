from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Any
from uuid import UUID

from app.core.database import get_db
from app.api.deps import get_current_active_user, RoleChecker
from app.models.user import User

from app.schemas.inventory import (
    ProcurementRequestCreate,
    ProcurementRequestResponse,
    ProcurementSummary
)
from app.services.procurement_service import ProcurementService
from app.schemas.common import SuccessResponse, PaginatedResponse, PaginationMeta

router = APIRouter()

@router.get("/requests", response_model=PaginatedResponse[ProcurementRequestResponse])
def get_procurement_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = None,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    service = ProcurementService(db)
    skip = (page - 1) * page_size
    reqs, total = service.repository.get_all(skip=skip, limit=page_size, status=status, search=search)
    return PaginatedResponse(
        success=True,
        data=[ProcurementRequestResponse.model_validate(r) for r in reqs],
        pagination=PaginationMeta(total_items=total, page=page, page_size=page_size, total_pages=(total + page_size - 1) // page_size)
    )

@router.get("/summary", response_model=SuccessResponse)
def get_procurement_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    service = ProcurementService(db)
    summary = service.get_summary()
    return SuccessResponse(success=True, message="Success", data=summary.model_dump())

@router.get("/search", response_model=SuccessResponse)
def search_procurement(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    service = ProcurementService(db)
    reqs, _ = service.repository.get_all(skip=0, limit=50, search=query)
    return SuccessResponse(
        success=True,
        message="Search results",
        data=[ProcurementRequestResponse.model_validate(r).model_dump() for r in reqs]
    )

@router.get("/filter", response_model=SuccessResponse)
def filter_procurement(
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    service = ProcurementService(db)
    reqs, _ = service.repository.get_all(skip=0, limit=100, status=status)
    return SuccessResponse(
        success=True,
        message="Filter results",
        data=[ProcurementRequestResponse.model_validate(r).model_dump() for r in reqs]
    )

@router.post("/create-request", response_model=SuccessResponse)
def create_procurement_request(
    data: ProcurementRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    service = ProcurementService(db)
    req = service.create_request(data, current_user)
    return SuccessResponse(
        success=True,
        message="Procurement request created successfully",
        data=ProcurementRequestResponse.model_validate(req).model_dump()
    )

@router.post("/approve-request", response_model=SuccessResponse)
def approve_procurement_request(
    req_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["Super Admin", "Administrator", "Fleet Manager"]))
) -> Any:
    service = ProcurementService(db)
    req = service.approve_request(req_id, current_user)
    return SuccessResponse(
        success=True,
        message="Procurement request approved successfully",
        data=ProcurementRequestResponse.model_validate(req).model_dump()
    )

@router.post("/reject-request", response_model=SuccessResponse)
def reject_procurement_request(
    req_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["Super Admin", "Administrator", "Fleet Manager"]))
) -> Any:
    service = ProcurementService(db)
    req = service.reject_request(req_id, current_user)
    return SuccessResponse(
        success=True,
        message="Procurement request rejected successfully",
        data=ProcurementRequestResponse.model_validate(req).model_dump()
    )
