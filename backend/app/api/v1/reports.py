"""
API endpoints for Reports.
"""
from datetime import date
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, PermissionChecker
from app.models.user import User
from app.schemas.report import ReportResponse
from app.services.report_service import ReportService


router = APIRouter()


def _handle_response(service: ReportService, data: list, export_format: str, title: str, current_user: User = None):
    """Helper to return JSON or export formats."""
    if export_format == "json":
        return ReportResponse(
            report_type=title,
            metadata={"count": len(data)},
            data=data
        )
        
    buffer, media_type, filename = service.export_data(data, export_format, title, current_user)
    
    # All exports now return BytesIO buffers
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename.split('.')[0]}_{__import__('datetime').datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.{filename.split('.')[1]}"}
    )


@router.get("/fleet")
def get_fleet_report(
    status: Optional[str] = Query(None),
    export_format: str = Query("json", description="json, csv, xlsx, pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("reports", "read"))
):
    service = ReportService(db)
    data = service.generate_fleet_report(status=status)
    return _handle_response(service, data, export_format, "Fleet Report", current_user)


@router.get("/drivers")
def get_driver_report(
    status: Optional[str] = Query(None),
    export_format: str = Query("json", description="json, csv, xlsx, pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("reports", "read"))
):
    service = ReportService(db)
    data = service.generate_driver_report(status=status)
    return _handle_response(service, data, export_format, "Driver Report", current_user)


@router.get("/trips")
def get_trip_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    export_format: str = Query("json", description="json, csv, xlsx, pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("reports", "read"))
):
    service = ReportService(db)
    data = service.generate_trip_report(start_date=start_date, end_date=end_date, status=status)
    return _handle_response(service, data, export_format, "Trip Report", current_user)


@router.get("/maintenance")
def get_maintenance_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    export_format: str = Query("json", description="json, csv, xlsx, pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("reports", "read"))
):
    service = ReportService(db)
    data = service.generate_maintenance_report(start_date=start_date, end_date=end_date, status=status)
    return _handle_response(service, data, export_format, "Maintenance Report", current_user)


@router.get("/fuel")
def get_fuel_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    export_format: str = Query("json", description="json, csv, xlsx, pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("reports", "read"))
):
    service = ReportService(db)
    data = service.generate_fuel_report(start_date=start_date, end_date=end_date)
    return _handle_response(service, data, export_format, "Fuel Report", current_user)


@router.get("/expenses")
def get_expense_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[str] = Query(None),
    export_format: str = Query("json", description="json, csv, xlsx, pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("reports", "read"))
):
    service = ReportService(db)
    data = service.generate_expense_report(start_date=start_date, end_date=end_date, status=status)
    return _handle_response(service, data, export_format, "Expense Report", current_user)


@router.get("/financial")
def get_financial_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    export_format: str = Query("json", description="json, csv, xlsx, pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("reports", "read"))
):
    service = ReportService(db)
    data = service.generate_financial_summary(start_date=start_date, end_date=end_date)
    return _handle_response(service, data, export_format, "Financial Summary Report", current_user)
