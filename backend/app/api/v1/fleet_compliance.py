from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.api.deps import get_db, PermissionChecker
from app.models.user import User
from app.services.fleet_compliance_service import FleetComplianceService

router = APIRouter()

@router.get("", response_model=dict)
def get_fleet_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = FleetComplianceService(db)
    return service.get_list()

@router.get("/summary", response_model=dict)
def get_fleet_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = FleetComplianceService(db)
    return service.get_summary(current_user)

@router.get("/analytics", response_model=dict)
def get_fleet_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = FleetComplianceService(db)
    return service.get_analytics()

@router.get("/export/csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = FleetComplianceService(db)
    csv_data = service.export_csv()
    return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=fleet_compliance_{__import__('datetime').datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"})

@router.get("/export/pdf")
def export_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = FleetComplianceService(db)
    pdf_data = service.export_pdf()
    return Response(content=pdf_data, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=fleet_compliance_{__import__('datetime').datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"})
