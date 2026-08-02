"""
Job Repository for database access.
"""
from typing import List, Tuple, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime

from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate


class JobRepository:
    """Repository for Job operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, job_id: UUID) -> Optional[Job]:
        return self.db.query(Job).filter(Job.id == job_id).first()

    def get_by_job_number(self, job_number: str) -> Optional[Job]:
        return self.db.query(Job).filter(Job.job_number == job_number).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
        unassigned_only: bool = False
    ) -> Tuple[List[Job], int]:
        query = self.db.query(Job)

        if status:
            query = query.filter(Job.status == status)

        if priority:
            query = query.filter(Job.priority == priority)

        if unassigned_only:
            query = query.filter(Job.trip_id.is_(None))

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Job.job_number.ilike(search_pattern),
                    Job.customer_name.ilike(search_pattern),
                    Job.pickup_address.ilike(search_pattern),
                    Job.delivery_address.ilike(search_pattern),
                    Job.cargo_description.ilike(search_pattern)
                )
            )

        total = query.count()
        items = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

        return items, total

    def generate_job_number(self) -> str:
        year = datetime.now().year
        count = self.db.query(Job).count() + 1
        return f"JOB-{year}-{count:05d}"

    def create(self, job_data: JobCreate, created_by_id: Optional[UUID] = None) -> Job:
        job_number = self.generate_job_number()
        
        # Ensure job number uniqueness
        while self.get_by_job_number(job_number):
            count = int(job_number.split('-')[-1]) + 1
            job_number = f"JOB-{datetime.now().year}-{count:05d}"

        job = Job(
            job_number=job_number,
            customer_name=job_data.customer_name,
            customer_contact=job_data.customer_contact,
            pickup_address=job_data.pickup_address,
            delivery_address=job_data.delivery_address,
            pickup_latitude=job_data.pickup_latitude,
            pickup_longitude=job_data.pickup_longitude,
            delivery_latitude=job_data.delivery_latitude,
            delivery_longitude=job_data.delivery_longitude,
            cargo_description=job_data.cargo_description,
            cargo_weight_kg=job_data.cargo_weight_kg,
            cargo_volume_cbm=job_data.cargo_volume_cbm,
            priority=job_data.priority,
            time_window_start=job_data.time_window_start,
            time_window_end=job_data.time_window_end,
            special_instructions=job_data.special_instructions,
            status="Pending",
            created_by_id=created_by_id
        )

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def update(self, job: Job, job_data: JobUpdate) -> Job:
        update_dict = job_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(job, field, value)

        self.db.commit()
        self.db.refresh(job)
        return job

    def delete(self, job: Job) -> None:
        self.db.delete(job)
        self.db.commit()
