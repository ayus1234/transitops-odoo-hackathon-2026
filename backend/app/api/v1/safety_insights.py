from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db, PermissionChecker
from app.models.user import User
from app.services.safety_insights_service import SafetyInsightsService

router = APIRouter()

def get_target_user_id(current_user: User) -> Optional[str]:
    if hasattr(current_user, 'role') and current_user.role and current_user.role.name == "Driver":
        return str(current_user.id)
    return None

@router.get("", response_model=dict)
@router.get("/rankings", response_model=dict)
def get_safety_rankings(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=1000),
    search: Optional[str] = None,
    filter_perf: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = SafetyInsightsService(db)
    user_id = get_target_user_id(current_user)
    return service.get_rankings(skip, limit, search, filter_perf, user_id, current_user)

@router.get("/summary", response_model=dict)
def get_safety_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = SafetyInsightsService(db)
    user_id = get_target_user_id(current_user)
    return service.get_summary(user_id)

@router.get("/analytics", response_model=dict)
def get_safety_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = SafetyInsightsService(db)
    # Analytics are fleet-wide or driver specific depending on implementation.
    # We will just return the generic analytics.
    return service.get_analytics()

@router.get("/alerts", response_model=dict)
def get_safety_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = SafetyInsightsService(db)
    user_id = get_target_user_id(current_user)
    return service.get_alerts(skip, limit, user_id)

@router.get("/export/csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = SafetyInsightsService(db)
    user_id = get_target_user_id(current_user)
    csv_data = service.export_csv(user_id)
    return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=safety_insights_{__import__('datetime').datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"})

@router.get("/export/pdf")
def export_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("dashboard", "read"))
):
    service = SafetyInsightsService(db)
    user_id = get_target_user_id(current_user)
    pdf_data = service.export_pdf(user_id)
    return Response(content=pdf_data, media_type="application/json", headers={"Content-Disposition": f"attachment; filename=safety_insights_{__import__('datetime').datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"})
