"""
Maintenance Tasks API endpoints.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, PermissionChecker
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.technician_workload import TaskSummaryResponse, TaskDetail, TaskAssignRequest
from app.services.technician_workload_service import TechnicianWorkloadService

router = APIRouter()

@router.get("", response_model=SuccessResponse)
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Get all maintenance tasks."""
    service = TechnicianWorkloadService(db)
    tasks = service.get_all_tasks(current_user=current_user)
    return SuccessResponse(success=True, message="Success", data=tasks)

@router.get("/summary", response_model=SuccessResponse)
def get_tasks_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Get task workload summary."""
    service = TechnicianWorkloadService(db)
    summary = service.get_task_summary(current_user=current_user)
    return SuccessResponse(success=True, message="Success", data=summary.model_dump())

@router.get("/search", response_model=SuccessResponse)
def search_tasks(
    q: str = Query(..., description="Search query"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Search tasks."""
    service = TechnicianWorkloadService(db)
    tasks = service.get_all_tasks(current_user=current_user, search=q)
    return SuccessResponse(success=True, message="Success", data=tasks)

@router.get("/filter", response_model=SuccessResponse)
def filter_tasks(
    status: Optional[str] = Query(None, description="Status filter"),
    technician: Optional[str] = Query(None, description="Technician Name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Filter tasks."""
    service = TechnicianWorkloadService(db)
    tasks = service.get_all_tasks(current_user=current_user, status=status, tech_name=technician)
    return SuccessResponse(success=True, message="Success", data=tasks)

@router.get("/export", response_class=Response)
def export_tasks(
    format: str = Query("csv", description="Export format (csv or pdf)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Export tasks list."""
    service = TechnicianWorkloadService(db)
    tasks = service.get_all_tasks(current_user=current_user)
    
    if format.lower() == "pdf":
        pdf_bytes = service.export_tasks_pdf(tasks)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=tasks_{__import__('datetime').datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"}
        )
    else:
        csv_str = service.export_tasks_csv(tasks)
        return Response(
            content=csv_str,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=tasks_{__import__('datetime').datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"}
        )

@router.post("/{task_id}/assign", response_model=SuccessResponse)
def assign_technician_to_task(
    task_id: UUID,
    req: TaskAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "update"))
):
    """Assign a technician to a task to trigger notifications and activity logs."""
    service = TechnicianWorkloadService(db)
    try:
        task = service.assign_technician(task_id, req, current_user)
        return SuccessResponse(success=True, message="Technician assigned successfully", data=task.model_dump())
    except ValueError as e:
        return SuccessResponse(success=False, message=str(e), data=None)
