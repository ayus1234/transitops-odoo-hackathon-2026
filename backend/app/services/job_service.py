"""
Job Business Service Layer.
"""
from typing import List, Tuple, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate
from app.repositories.job_repository import JobRepository
from app.utils.exceptions import NotFoundError, BusinessLogicError


class JobService:
    """Service for job business operations."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = JobRepository(db)

    def get_job(self, job_id: UUID) -> Job:
        job = self.repository.get_by_id(job_id)
        if not job:
            raise NotFoundError(f"Job with ID {job_id} not found")
        return job

    def get_job_by_number(self, job_number: str) -> Optional[Job]:
        return self.repository.get_by_job_number(job_number)

    def get_jobs(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
        unassigned_only: bool = False
    ) -> Tuple[List[Job], int]:
        skip = (page - 1) * page_size
        return self.repository.get_all(
            skip=skip,
            limit=page_size,
            status=status,
            priority=priority,
            search=search,
            unassigned_only=unassigned_only
        )

    def create_job(self, job_data: JobCreate, created_by_id: Optional[UUID] = None) -> Job:
        from app.services.audit_event_service import AuditEventService

        # Validate time windows
        if (job_data.time_window_start and job_data.time_window_end and
            job_data.time_window_end <= job_data.time_window_start):
            raise BusinessLogicError(
                "Time window end date/time must be after time window start date/time",
                code="BIZ_JOB_001"
            )

        job = self.repository.create(job_data, created_by_id=created_by_id)
        
        try:
            audit = AuditEventService(self.db)
            audit.record_event(
                event_type="JOB_CREATED",
                entity_type="Job",
                entity_id=UUID(str(job.id)),
                job_id=UUID(str(job.id)),
                actor_id=created_by_id,
                summary=f"Customer Job {job.job_number} created for {job.customer_name}",
                payload={
                    "customer_name": job.customer_name,
                    "pickup_address": job.pickup_address,
                    "delivery_address": job.delivery_address,
                    "cargo_weight_kg": float(str(job.cargo_weight_kg)) if job.cargo_weight_kg is not None else 0.0,
                    "priority": job.priority
                }
            )
        except Exception:
            pass  # Non-blocking event logging

        return job

    def update_job(self, job_id: UUID, job_data: JobUpdate) -> Job:
        job = self.get_job(job_id)

        # Cannot edit cancelled or delivered jobs
        if job.status in ("Delivered", "Cancelled"):
            raise BusinessLogicError(
                f"Cannot modify job {job.job_number} in '{job.status}' state",
                code="BIZ_JOB_002"
            )

        return self.repository.update(job, job_data)

    def cancel_job(self, job_id: UUID, reason: Optional[str] = None) -> Job:
        job = self.get_job(job_id)

        if job.status == "Delivered":
            raise BusinessLogicError(
                f"Cannot cancel job {job.job_number} because it has already been delivered",
                code="BIZ_JOB_003"
            )

        job.status = "Cancelled"
        if reason:
            job.special_instructions = f"{job.special_instructions or ''}\n[Cancellation Reason]: {reason}".strip()

        self.db.commit()
        self.db.refresh(job)
        return job

    def delete_job(self, job_id: UUID) -> None:
        job = self.get_job(job_id)
        if job.status in ("In Transit", "Assigned"):
            raise BusinessLogicError(
                f"Cannot delete job {job.job_number} that is currently '{job.status}'",
                code="BIZ_JOB_004"
            )

        self.repository.delete(job)
