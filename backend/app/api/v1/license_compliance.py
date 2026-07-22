from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db, PermissionChecker
from app.models.user import User
from app.services.license_compliance_service import LicenseComplianceService

router = APIRouter()

def get_target_user_id(current_user: User) -> Optional[str]:
    # Role structure assumption based on hackathon scope
    if hasattr(current_user, 'role') and current_user.role and current_user.role.name == "Driver":
        return str(current_user.id)
    return None

@router.get("", response_model=dict)
def get_license_compliance(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=1000),
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = LicenseComplianceService(db)
    user_id = get_target_user_id(current_user)
    return service.get_paginated_compliance(skip, limit, search, status_filter, user_id, current_user)

@router.get("/summary", response_model=dict)
def get_license_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = LicenseComplianceService(db)
    user_id = get_target_user_id(current_user)
    return service.get_summary(user_id)

@router.get("/search", response_model=dict)
def search_license_compliance(
    search: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = LicenseComplianceService(db)
    user_id = get_target_user_id(current_user)
    return service.get_paginated_compliance(0, 100, search, None, user_id, current_user)

@router.get("/filter", response_model=dict)
def filter_license_compliance(
    status_filter: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = LicenseComplianceService(db)
    user_id = get_target_user_id(current_user)
    return service.get_paginated_compliance(0, 100, None, status_filter, user_id, current_user)

@router.get("/export/csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = LicenseComplianceService(db)
    user_id = get_target_user_id(current_user)
    csv_data = service.export_csv(user_id)
    return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=license_compliance_{__import__('datetime').datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"})

@router.get("/export/pdf")
def export_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = LicenseComplianceService(db)
    user_id = get_target_user_id(current_user)
    pdf_data = service.export_pdf(user_id)
    return Response(content=pdf_data, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=license_compliance_{__import__('datetime').datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"})
