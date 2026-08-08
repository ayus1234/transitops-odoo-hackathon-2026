"""
Logistics CRM API Router.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import PermissionChecker
from app.models.user import User
from app.schemas.crm import ClientAccount
from app.services.crm_service import CRMService

router = APIRouter(prefix="/crm", tags=["Logistics CRM & Client Accounts"])


@router.get("/clients", response_model=List[ClientAccount])
def get_client_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("jobs", "read"))
):
    """Get customer client accounts and rate cards."""
    service = CRMService(db)
    return service.get_client_accounts()
