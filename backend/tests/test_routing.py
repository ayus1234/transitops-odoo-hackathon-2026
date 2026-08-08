"""
Unit tests for Priority 2 — Routing & ETA Adapter Service.
"""
import pytest
from datetime import datetime, timedelta, date
from uuid import UUID
from decimal import Decimal

from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.user import User
from app.models.role import Role
from app.models.trip import Trip
from app.models.trip_stop import TripStop
from app.schemas.routing import (
    RouteCalculationRequest,
    CoordinateLocation
)
from app.services.routing.routing_service import RoutingService
from app.services.routing.haversine_provider import HaversineFallbackProvider
from app.services.routing.osrm_provider import OSRMProvider


def test_haversine_provider_distance_and_legs():
    provider = HaversineFallbackProvider()
    origin = (19.0760, 72.8777)  # Mumbai
    dest = (18.5204, 73.8567)    # Pune

    result = provider.calculate_route(origin, dest, average_speed_kmh=60.0)

    assert result["total_distance_km"] > 110.0  # Approx road distance
    assert result["total_duration_minutes"] > 100.0
    assert len(result["legs"]) == 1
    assert "polyline_geometry" in result


def test_routing_service_calculate_route_with_waypoints(db_session):
    service = RoutingService(db_session, provider=HaversineFallbackProvider())

    req = RouteCalculationRequest(
        origin=CoordinateLocation(latitude=19.0760, longitude=72.8777, name="Mumbai BKC"),
        destination=CoordinateLocation(latitude=18.5204, longitude=73.8567, name="Pune Depot"),
        waypoints=[
            CoordinateLocation(latitude=18.9220, longitude=72.8347, name="Colaba Stop")
        ],
        average_speed_kmh=65.0
    )

    res = service.calculate_route(req)

    assert res.total_distance_km > 0.0
    assert res.total_duration_minutes > 0.0
    assert len(res.legs) == 2
    assert res.provider_used == "Haversine Heuristic"


def test_routing_service_multi_stop_eta_calculation(db_session):
    service = RoutingService(db_session, provider=HaversineFallbackProvider())

    role = db_session.query(Role).first()
    if not role:
        role = Role(name="Driver", permissions={})
        db_session.add(role)
        db_session.commit()

    ts = int(datetime.now().timestamp() * 1000)

    # 1. Create Vehicle & Driver
    vehicle = Vehicle(
        registration_number=f"ROUTE-{ts}",
        vehicle_name="Routing Test Truck",
        vehicle_type="Truck",
        capacity_kg=15000.00,
        fuel_type="Diesel",
        status="Available"
    )
    db_session.add(vehicle)

    user = User(
        email=f"route.driver.{ts}@transitops.com",
        password_hash="hash",
        first_name="Route",
        last_name="Driver",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    driver = Driver(
        user_id=user.id,
        license_number=f"LIC-RTE-{ts}",
        license_category="Heavy Vehicle",
        license_issue_date=date(2020, 1, 1),
        date_of_birth=date(1990, 1, 1),
        status="Available",
        license_expiry_date=date(2035, 1, 1)
    )
    db_session.add(driver)
    db_session.commit()

    # 2. Create Multi-Stop Trip
    now = datetime.now()
    trip = Trip(
        trip_number=f"TRP-RTE-{ts}",
        vehicle_id=vehicle.id,
        driver_id=driver.id,
        source="Mumbai BKC Hub",
        destination="Pune Phugewadi Depot",
        cargo_weight_kg=Decimal("5000.00"),
        planned_distance_km=Decimal("150.0"),
        planned_departure=now,
        planned_arrival=now + timedelta(hours=4),
        status="Draft"
    )
    db_session.add(trip)
    db_session.commit()

    # 3. Create 3 TripStops
    stop1 = TripStop(
        trip_id=trip.id,
        sequence=1,
        location_name="Mumbai BKC Hub",
        latitude=Decimal("19.0760"),
        longitude=Decimal("72.8777"),
        stop_type="Origin",
        status="Pending"
    )
    stop2 = TripStop(
        trip_id=trip.id,
        sequence=2,
        location_name="Lonavala Expressway Rest",
        latitude=Decimal("18.7557"),
        longitude=Decimal("73.4091"),
        stop_type="Waypoint",
        status="Pending"
    )
    stop3 = TripStop(
        trip_id=trip.id,
        sequence=3,
        location_name="Pune Phugewadi Depot",
        latitude=Decimal("18.5204"),
        longitude=Decimal("73.8567"),
        stop_type="Destination",
        status="Pending"
    )
    db_session.add_all([stop1, stop2, stop3])
    db_session.commit()

    # Calculate Multi-Stop ETA
    eta_res = service.calculate_multi_stop_eta(UUID(str(trip.id)))

    assert eta_res.trip_id == UUID(str(trip.id))
    assert eta_res.total_distance_km > 100.0
    assert len(eta_res.stops) == 3

    # Check ETAs are chronologically ordered
    assert eta_res.stops[0].planned_arrival <= eta_res.stops[0].planned_departure
    assert eta_res.stops[0].planned_departure < eta_res.stops[1].planned_arrival
    assert eta_res.stops[1].planned_arrival < eta_res.stops[1].planned_departure
    assert eta_res.stops[1].planned_departure < eta_res.stops[2].planned_arrival

    # Verify DB trip update
    db_session.refresh(trip)
    assert float(str(trip.planned_distance_km)) > 100.0
    assert trip.planned_arrival is not None
