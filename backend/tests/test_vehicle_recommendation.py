"""
Unit tests for Priority 1 — Vehicle & Driver Intelligent Recommendation Engine.
"""
import pytest
from datetime import datetime, date
from uuid import UUID

from app.models.user import User
from app.models.role import Role
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.job import Job
from app.models.maintenance import Maintenance
from app.schemas.job import JobCreate
from app.schemas.vehicle import VehicleCreate
from app.services.job_service import JobService
from app.services.vehicle_service import VehicleService
from app.services.vehicle_recommendation_service import VehicleRecommendationService


def test_vehicle_recommendation_ranking_and_capacity_fit(db_session):
    job_service = JobService(db_session)
    vehicle_service = VehicleService(db_session)
    recommendation_service = VehicleRecommendationService(db_session)

    # Fetch/create driver role
    role = db_session.query(Role).first()
    if not role:
        role = Role(name="Driver", permissions={})
        db_session.add(role)
        db_session.commit()

    ts = int(datetime.now().timestamp() * 1000)

    # 1. Create Job requiring 8,000 kg cargo
    job = job_service.create_job(JobCreate(
        customer_name=f"Rec Test Corp {ts}",
        pickup_address="Bandra Kurla Complex, Mumbai",
        delivery_address="Phugewadi, Pune",
        cargo_weight_kg=8000.00
    ))

    # 2. Vehicle A: Optimal Payload (10,000 kg capacity -> 80% fill ratio -> 100 pts)
    v_optimal = vehicle_service.create_vehicle(VehicleCreate(
        registration_number=f"OPT-{ts}",
        vehicle_name="Optimal Delivery Truck",
        vehicle_type="Truck",
        capacity_kg=10000.00,
        fuel_type="Diesel",
        status="Available"
    ))

    # 3. Vehicle B: Oversized Payload (50,000 kg capacity -> 16% fill ratio -> penalized)
    v_oversized = vehicle_service.create_vehicle(VehicleCreate(
        registration_number=f"OVER-{ts}",
        vehicle_name="Massive Trailer",
        vehicle_type="Trailer",
        capacity_kg=50000.00,
        fuel_type="Diesel",
        status="Available"
    ))

    # 4. Vehicle C: Over-Capacity (5,000 kg capacity -> Disqualified)
    v_small = vehicle_service.create_vehicle(VehicleCreate(
        registration_number=f"SMALL-{ts}",
        vehicle_name="Mini Pickup",
        vehicle_type="Van",
        capacity_kg=5000.00,
        fuel_type="Diesel",
        status="Available"
    ))

    # 5. Create Driver
    user = User(
        email=f"rec.driver.{ts}@transitops.com",
        password_hash="hash",
        first_name="Rec",
        last_name="Driver",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    driver = Driver(
        user_id=user.id,
        license_number=f"LIC-REC-{ts}",
        license_category="Heavy Vehicle",
        license_issue_date=date(2020, 1, 1),
        date_of_birth=date(1990, 1, 1),
        status="Available",
        license_expiry_date=date(2035, 1, 1)
    )
    db_session.add(driver)
    db_session.commit()

    # Get Recommendations
    res = recommendation_service.recommend_vehicles_for_job(UUID(str(job.id)), top_n=5)

    assert res.job_id == UUID(str(job.id))
    assert res.cargo_weight_kg == 8000.00
    assert len(res.recommendations) >= 2

    # Verify Vehicle C (mini pickup) was disqualified (capacity 5000 < 8000)
    rec_v_ids = [r.vehicle_id for r in res.recommendations]
    assert UUID(str(v_small.id)) not in rec_v_ids

    # Top recommendation should be Vehicle A (optimal payload fit)
    top = res.recommendations[0]
    assert top.vehicle_id == UUID(str(v_optimal.id))
    assert top.score_breakdown.capacity_score == 100.0
    assert top.overall_match_score > res.recommendations[1].overall_match_score
    assert top.suggested_driver_id == UUID(str(driver.id))


def test_vehicle_recommendation_health_deduction(db_session):
    job_service = JobService(db_session)
    vehicle_service = VehicleService(db_session)
    recommendation_service = VehicleRecommendationService(db_session)

    ts = int(datetime.now().timestamp() * 1000)

    job = job_service.create_job(JobCreate(
        customer_name=f"Health Test {ts}",
        pickup_address="Delhi",
        delivery_address="Noida",
        cargo_weight_kg=2000.00
    ))

    v_sick = vehicle_service.create_vehicle(VehicleCreate(
        registration_number=f"SICK-{ts}",
        vehicle_name="Sick Van",
        vehicle_type="Van",
        capacity_kg=5000.00,
        fuel_type="Diesel",
        status="Available"
    ))

    # Add open critical maintenance record
    maint = Maintenance(
        vehicle_id=v_sick.id,
        maintenance_number=f"MNT-CRIT-{ts}",
        maintenance_type="Engine Repair",
        description="Engine Overhaul Needed",
        status="In Progress",
        priority="Critical",
        scheduled_date=date.today()
    )
    db_session.add(maint)
    db_session.commit()

    res = recommendation_service.recommend_vehicles_for_job(UUID(str(job.id)))

    sick_rec = next((r for r in res.recommendations if r.vehicle_id == UUID(str(v_sick.id))), None)
    assert sick_rec is not None
    assert sick_rec.score_breakdown.health_score < 100.0
    assert any("Open High-Priority Maintenance" in reason for reason in sick_rec.match_reasons)
