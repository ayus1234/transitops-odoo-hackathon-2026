"""
Proof of Delivery (POD) API Router.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import UUID4

from app.core.database import get_db
from app.api.deps import PermissionChecker, get_current_user
from app.models.user import User
from app.schemas.pod import PODSubmissionRequest, PODResponse
from app.services.pod_service import PODService
from app.utils.exceptions import NotFoundError, BusinessLogicError

router = APIRouter(prefix="/pod", tags=["Proof of Delivery (POD)"])


@router.post("/stops/{stop_id}/submit", response_model=PODResponse)
def submit_proof_of_delivery(
    stop_id: UUID4,
    request: PODSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "update"))
):
    """Submit digital Proof of Delivery (signature, photo proof, receiver name, GPS geofence verification)."""
    service = PODService(db)
    try:
        return service.submit_proof_of_delivery(stop_id=stop_id, req=request)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessLogicError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/stops/{stop_id}", response_model=PODResponse)
def get_proof_of_delivery(
    stop_id: UUID4,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "read"))
):
    """Get Proof of Delivery verification records for a trip stop."""
    service = PODService(db)
    try:
        return service.get_proof_of_delivery(stop_id=stop_id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
