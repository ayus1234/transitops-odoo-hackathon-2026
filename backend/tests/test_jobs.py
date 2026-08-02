"""
Unit tests for Jobs & Customer Orders (Feature 2.1).
"""
import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate
from app.services.job_service import JobService
from app.utils.exceptions import NotFoundError, BusinessLogicError


def test_create_job_success(db_session):
    service = JobService(db_session)
    job_data = JobCreate(
        customer_name="Acme Logistics India",
        customer_contact="+91 98765 43210",
        pickup_address="Bhiwandi Warehouse Depot, Maharashtra",
        delivery_address="Navi Mumbai Port Terminal, Maharashtra",
        cargo_description="Electronic Components & Semiconductors",
        cargo_weight_kg=12500.50,
        cargo_volume_cbm=45.0,
        priority="High",
        special_instructions="Handle with care. Temperature controlled."
    )

    job = service.create_job(job_data)

    assert job.id is not None
    assert job.job_number.startswith("JOB-")
    assert job.customer_name == "Acme Logistics India"
    assert job.cargo_weight_kg == 12500.50
    assert job.status == "Pending"
    assert job.priority == "High"


def test_create_job_invalid_time_window(db_session):
    service = JobService(db_session)
    now = datetime.now()
    job_data = JobCreate(
        customer_name="FastTrack Retail",
        pickup_address="Delhi NCR Hub",
        delivery_address="Jaipur Depot",
        time_window_start=now,
        time_window_end=now - timedelta(hours=2)  # Invalid: end before start
    )

    with pytest.raises(BusinessLogicError) as exc_info:
        service.create_job(job_data)

    assert "Time window end date/time must be after" in str(exc_info.value)


def test_list_and_search_jobs(db_session):
    service = JobService(db_session)

    j1 = service.create_job(JobCreate(
        customer_name="Global Express",
        pickup_address="Mumbai",
        delivery_address="Pune",
        priority="Urgent"
    ))

    j2 = service.create_job(JobCreate(
        customer_name="Local Retailers",
        pickup_address="Nagpur",
        delivery_address="Nashik",
        priority="Low"
    ))

    items, total = service.get_jobs(priority="Urgent")
    assert total == 1
    assert items[0].id == j1.id

    items_search, total_search = service.get_jobs(search="Global")
    assert total_search == 1
    assert items_search[0].id == j1.id


def test_update_job_status(db_session):
    service = JobService(db_session)
    job = service.create_job(JobCreate(
        customer_name="Reliance Freight",
        pickup_address="Surat",
        delivery_address="Ahmedabad"
    ))

    updated = service.update_job(job.id, JobUpdate(status="Assigned"))
    assert updated.status == "Assigned"


def test_cancel_job(db_session):
    service = JobService(db_session)
    job = service.create_job(JobCreate(
        customer_name="Tata Motors Supply",
        pickup_address="Pune Plant",
        delivery_address="Chennai Port"
    ))

    cancelled = service.cancel_job(job.id, reason="Customer cancelled booking")
    assert cancelled.status == "Cancelled"
    assert "Customer cancelled booking" in cancelled.special_instructions


def test_delete_job_blocked_when_in_transit(db_session):
    service = JobService(db_session)
    job = service.create_job(JobCreate(
        customer_name="Mahindra Freight",
        pickup_address="Nashik",
        delivery_address="Indore"
    ))

    service.update_job(job.id, JobUpdate(status="In Transit"))

    with pytest.raises(BusinessLogicError) as exc_info:
        service.delete_job(job.id)

    assert "Cannot delete job" in str(exc_info.value)
