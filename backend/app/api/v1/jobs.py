"""
Jobs API Router.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
import math

from app.core.database import get_db
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobListResponse
from app.services.job_service import JobService
from app.api.deps import PermissionChecker, get_current_user
from app.models.user import User

router = APIRouter(prefix="/jobs", tags=["Jobs & Customer Orders"])


@router.get("", response_model=JobListResponse)
def list_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status (Draft, Pending, Assigned, In Transit, Delivered, Cancelled)"),
    priority: Optional[str] = Query(None, description="Filter by priority (Low, Normal, High, Urgent)"),
    search: Optional[str] = Query(None, description="Search by job number, customer, address or cargo"),
    unassigned_only: bool = Query(False, description="Filter for unassigned jobs only"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "read"))
):
    """Get customer jobs with pagination and filters."""
    service = JobService(db)
    items, total = service.get_jobs(
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        search=search,
        unassigned_only=unassigned_only
    )
    pages = math.ceil(total / page_size) if total > 0 else 1
    return JobListResponse(
        items=[JobResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        size=page_size,
        pages=pages
    )


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "create"))
):
    """Create a new customer shipping order / job."""
    service = JobService(db)
    job = service.create_job(job_data, created_by_id=current_user.id)
    return JobResponse.model_validate(job)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "read"))
):
    """Get job details by ID."""
    service = JobService(db)
    job = service.get_job(job_id)
    return JobResponse.model_validate(job)


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: UUID,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "update"))
):
    """Update job details."""
    service = JobService(db)
    job = service.update_job(job_id, job_data)
    return JobResponse.model_validate(job)


@router.post("/{job_id}/cancel", response_model=JobResponse)
def cancel_job(
    job_id: UUID,
    reason: Optional[str] = Query(None, description="Reason for cancellation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "update"))
):
    """Cancel a customer job."""
    service = JobService(db)
    job = service.cancel_job(job_id, reason=reason)
    return JobResponse.model_validate(job)


@router.get("/track/{job_number}")
def track_job_public(
    job_number: str,
    db: Session = Depends(get_db)
):
    """Public tracking lookup by job/tracking number (no auth required for customer portal)."""
    service = JobService(db)
    job = service.get_job_by_number(job_number)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment/Job #{job_number} not found"
        )
    
    response_data = {
        "id": str(job.id),
        "job_number": job.job_number,
        "customer_name": job.customer_name,
        "source_address": job.source_address,
        "destination_address": job.destination_address,
        "cargo_description": job.cargo_description,
        "weight_kg": float(job.weight_kg) if job.weight_kg else 0.0,
        "priority": job.priority,
        "status": job.status,
        "pickup_window_start": job.pickup_window_start.isoformat() if job.pickup_window_start else None,
        "delivery_window_end": job.delivery_window_end.isoformat() if job.delivery_window_end else None,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "tracking_timeline": [
            {"status": "Created", "timestamp": job.created_at.isoformat() if job.created_at else None, "completed": True},
            {"status": "Assigned", "completed": job.status in ["Assigned", "In Transit", "Delivered"]},
            {"status": "In Transit", "completed": job.status in ["In Transit", "Delivered"]},
            {"status": "Delivered", "completed": job.status == "Delivered"}
        ]
    }
    
    if job.assigned_vehicle:
        response_data["vehicle"] = {
            "registration_number": job.assigned_vehicle.registration_number,
            "name": job.assigned_vehicle.vehicle_name,
            "type": job.assigned_vehicle.vehicle_type,
            "latitude": float(job.assigned_vehicle.latitude) if job.assigned_vehicle.latitude else None,
            "longitude": float(job.assigned_vehicle.longitude) if job.assigned_vehicle.longitude else None,
            "status": job.assigned_vehicle.status
        }
        
    if job.assigned_driver and job.assigned_driver.user:
        response_data["driver"] = {
            "first_name": job.assigned_driver.user.first_name,
            "phone_number": job.assigned_driver.user.phone_number
        }
        
    return response_data


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("trips", "delete"))
):
    """Delete a job."""
    service = JobService(db)
    service.delete_job(job_id)
    return None
