"""
Technician Workload Management API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, PermissionChecker
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.technician_workload import TechnicianSummaryResponse, TechnicianDetail
from app.services.technician_workload_service import TechnicianWorkloadService

router = APIRouter()

@router.get("", response_model=SuccessResponse)
def get_technicians(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Get all technicians."""
    service = TechnicianWorkloadService(db)
    technicians = service.get_all_technicians()
    return SuccessResponse(success=True, message="Success", data=technicians)

@router.get("/summary", response_model=SuccessResponse)
def get_technicians_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Get technician workload summary."""
    service = TechnicianWorkloadService(db)
    summary = service.get_technician_summary()
    return SuccessResponse(success=True, message="Success", data=summary.model_dump())

@router.get("/search", response_model=SuccessResponse)
def search_technicians(
    q: str = Query(..., description="Search query for name or ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Search technicians."""
    service = TechnicianWorkloadService(db)
    technicians = service.get_all_technicians(search=q)
    return SuccessResponse(success=True, message="Success", data=technicians)

@router.get("/filter", response_model=SuccessResponse)
def filter_technicians(
    status: Optional[str] = Query(None, description="Status filter (Available, Assigned, Busy)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Filter technicians."""
    service = TechnicianWorkloadService(db)
    technicians = service.get_all_technicians(status=status)
    return SuccessResponse(success=True, message="Success", data=technicians)

@router.get("/export", response_class=Response)
def export_technicians(
    format: str = Query("csv", description="Export format (csv or pdf)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("maintenance", "read"))
):
    """Export technicians list."""
    service = TechnicianWorkloadService(db)
    technicians = service.get_all_technicians()
    
    if format.lower() == "pdf":
        pdf_bytes = service.export_technicians_pdf(technicians)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=technicians_{__import__('datetime').datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"}
        )
    else:
        csv_str = service.export_technicians_csv(technicians)
        return Response(
            content=csv_str,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=technicians_{__import__('datetime').datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"}
        )
