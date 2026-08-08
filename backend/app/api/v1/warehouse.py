"""
Yard & Warehouse API Router.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import PermissionChecker
from app.models.user import User
from app.schemas.warehouse import WarehouseStagingSummary
from app.services.warehouse_service import WarehouseService

router = APIRouter(prefix="/warehouse", tags=["Yard & Warehouse Management"])


@router.get("/yard-staging", response_model=WarehouseStagingSummary)
def get_yard_staging_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("inventory", "read"))
):
    """Get warehouse loading dock bays occupancy and staging inventory."""
    service = WarehouseService(db)
    return service.get_yard_staging_summary()
