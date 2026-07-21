"""
Expense API endpoints.
"""
from typing import Optional, List
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, PermissionChecker
from app.models.user import User
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseStatusUpdate,
    ExpenseResponse,
    ExpenseListResponse
)
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.services.expense_service import ExpenseService


router = APIRouter()


# ============================================================
# COLLECTION ROUTES
# ============================================================

@router.get("", response_model=PaginatedResponse[ExpenseListResponse])
def list_expenses(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    expense_type: str | None = Query(None, description="Filter by expense type"),
    vehicle_id: UUID | None = Query(None, description="Filter by vehicle ID"),
    trip_id: UUID | None = Query(None, description="Filter by trip ID"),
    status: str | None = Query(None, description="Filter by status"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    search: str | None = Query(None, description="Search by description, vendor, or receipt"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("expenses", "read"))
):
    """
    Get list of expenses with pagination and filters.

    Permissions: expenses:read
    """
    service = ExpenseService(db)
    records, total = service.get_expenses(
        page=page,
        page_size=page_size,
        expense_type=expense_type,
        vehicle_id=vehicle_id,
        trip_id=trip_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        search=search
    )

    return PaginatedResponse(
        success=True,
        data=[ExpenseListResponse.model_validate(r) for r in records],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=(total + page_size - 1) // page_size
        )
    )


@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED
)
def create_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("expenses", "create"))
):
    """
    Create a new expense record.

    Permissions: expenses:create

    Business Rules:
    - At least one relation must be set (vehicle, trip, maintenance)
    - Amount > 0
    - Date not in future
    """
    service = ExpenseService(db)
    record = service.create_expense(data, recorded_by=current_user.id)
    return ExpenseResponse.model_validate(record)


# ============================================================
# SINGLE RESOURCE ROUTES
# ============================================================

@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("expenses", "read"))
):
    """
    Get expense by ID.

    Permissions: expenses:read
    """
    service = ExpenseService(db)
    record = service.get_expense(expense_id)
    return ExpenseResponse.model_validate(record)


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: UUID,
    data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("expenses", "update"))
):
    """
    Update an expense record.

    Permissions: expenses:update

    Business Rules:
    - Cannot update Approved expenses.
    """
    service = ExpenseService(db)
    record = service.update_expense(expense_id, data, current_user)
    return ExpenseResponse.model_validate(record)


@router.delete("/{expense_id}", response_model=SuccessResponse)
def delete_expense(
    expense_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("expenses", "delete"))
):
    """
    Delete an expense record.

    Permissions: expenses:delete

    Business Rules:
    - Cannot delete Approved expenses.
    """
    service = ExpenseService(db)
    service.delete_expense(expense_id, current_user)
    return SuccessResponse(
        success=True,
        message="Expense deleted successfully"
    )


# ============================================================
# LIFECYCLE ROUTES
# ============================================================

@router.patch("/{expense_id}/approve", response_model=ExpenseResponse)
def approve_expense(
    expense_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("expenses", "update"))
):
    """
    Approve an expense.

    Permissions: expenses:update
    """
    service = ExpenseService(db)
    record = service.approve_expense(expense_id, approved_by=current_user.id)
    return ExpenseResponse.model_validate(record)


@router.patch("/{expense_id}/reject", response_model=ExpenseResponse)
def reject_expense(
    expense_id: UUID,
    data: ExpenseStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("expenses", "update"))
):
    """
    Reject an expense.

    Permissions: expenses:update
    """
    service = ExpenseService(db)
    record = service.reject_expense(expense_id, data, current_user)
    return ExpenseResponse.model_validate(record)
