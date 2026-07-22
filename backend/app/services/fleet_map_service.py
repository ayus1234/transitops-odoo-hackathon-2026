from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import HTTPException
from datetime import datetime

from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.trip import Trip
from app.models.maintenance import Maintenance
from app.models.maintenance import Maintenance
from app.schemas.fleet_map import FullFleetMapResponse, VehicleMarker, DriverMarker, TripMarker, FleetMapBounds
from app.services.activity_service import activity_service
from app.schemas.activity import ActivityCreate
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum


class FleetMapService:
    def _apply_rbac_filter_query(self, db: Session, query: Any, model: Any, current_user: User):
        if not current_user.role:
            return query.filter(model.id == None)  # Return none if no role
        
        role_name = current_user.role.name.lower()
        if role_name == "driver":
            if model == Vehicle:
                # Driver can only see vehicles they are assigned to via active trips
                driver_rec = current_user.driver
                if not driver_rec:
                    return query.filter(model.id == None)
                active_trips = db.query(Trip).filter(Trip.driver_id == driver_rec.id, Trip.status == 'Dispatched').all()
                assigned_vehicle_ids = [t.vehicle_id for t in active_trips]
                return query.filter(model.id.in_(assigned_vehicle_ids))
            elif model == Driver:
                # Driver sees only themselves
                return query.filter(model.user_id == current_user.id)
            elif model == Trip:
                # Driver sees only their trips
                driver_rec = current_user.driver
                if not driver_rec:
                    return query.filter(model.id == None)
                return query.filter(model.driver_id == driver_rec.id)
        
        # Admin / Fleet Manager see all
        return query

    def get_full_fleet_map(self, db: Session, current_user: User) -> FullFleetMapResponse:
        vehicles = self._apply_rbac_filter_query(db, db.query(Vehicle), Vehicle, current_user).all()
        drivers = self._apply_rbac_filter_query(db, db.query(Driver), Driver, current_user).all()
        trips = self._apply_rbac_filter_query(db, db.query(Trip).filter(Trip.status == 'Dispatched'), Trip, current_user).all()

        # Batch query active trips for vehicles and drivers
        active_trips_for_v = db.query(Trip.vehicle_id, Trip.trip_number, User.first_name, User.last_name)\
            .join(Driver, Driver.id == Trip.driver_id)\
            .join(User, User.id == Driver.user_id)\
            .filter(Trip.status == 'Dispatched').all()
        trip_map = {t.vehicle_id: {"trip_number": t.trip_number, "driver_name": f"{t.first_name} {t.last_name}"} for t in active_trips_for_v}

        active_trips_for_d = db.query(Trip.driver_id, Trip.trip_number, Vehicle.vehicle_name)\
            .join(Vehicle, Vehicle.id == Trip.vehicle_id)\
            .filter(Trip.status == 'Dispatched').all()
        d_trip_map = {t.driver_id: {"trip_number": t.trip_number, "vehicle_name": t.vehicle_name} for t in active_trips_for_d}

        # Batch query critical alerts
        critical_alerts = set(r[0] for r in db.query(Maintenance.vehicle_id)\
            .filter(Maintenance.priority == 'Critical', Maintenance.status.in_(['Pending', 'Approved', 'In Progress'])).all())

        v_markers = []
        for v in vehicles:
            t_info = trip_map.get(v.id, {})
            v_markers.append(VehicleMarker(
                vehicle_id=v.id,
                vehicle_name=v.vehicle_name,
                registration_number=v.registration_number,
                latitude=float(v.latitude) if v.latitude else None,
                longitude=float(v.longitude) if v.longitude else None,
                status=v.status,
                driver_name=t_info.get("driver_name"),
                active_trip=t_info.get("trip_number"),
                has_critical_alert=v.id in critical_alerts,
                last_updated=v.updated_at
            ))

        d_markers = []
        for d in drivers:
            t_info = d_trip_map.get(d.id, {})
            driver_name_str = f"{d.user.first_name} {d.user.last_name}" if d.user else "Unknown Driver"
            
            d_markers.append(DriverMarker(
                driver_id=d.id,
                driver_name=driver_name_str,
                latitude=float(d.latitude) if d.latitude else None,
                longitude=float(d.longitude) if d.longitude else None,
                status=d.status,
                assigned_vehicle=t_info.get("vehicle_name"),
                active_trip=t_info.get("trip_number"),
                last_updated=d.updated_at
            ))

        t_markers = []
        for t in trips:
            t_markers.append(TripMarker(
                trip_id=t.id,
                origin=t.source,
                destination=t.destination,
                trip_status=t.status,
                estimated_arrival_time=t.estimated_arrival_time,
                vehicle_id=t.vehicle_id,
                driver_id=t.driver_id,
                route_information=t.route_information
            ))

        bounds = self._calculate_bounds(v_markers, d_markers)
        
        # Log activity
        activity_service.log_activity(
            db,
            ActivityCreate(
                module=ModuleEnum.DASHBOARD,
                activity_type=ActivityTypeEnum.SYSTEM,
                title="Fleet Map Accessed",
                description="User accessed the full fleet map.",
                user_id=str(current_user.id),
                severity=SeverityEnum.INFO
            )
        )

        return FullFleetMapResponse(
            vehicles=v_markers,
            drivers=d_markers,
            trips=t_markers,
            bounds=bounds
        )

    def _calculate_bounds(self, v_markers: List[VehicleMarker], d_markers: List[DriverMarker]) -> FleetMapBounds:
        lats = [m.latitude for m in v_markers + d_markers if m.latitude is not None]
        lngs = [m.longitude for m in v_markers + d_markers if m.longitude is not None]
        
        if not lats or not lngs:
            return FleetMapBounds()
            
        return FleetMapBounds(
            min_lat=min(lats),
            max_lat=max(lats),
            min_lng=min(lngs),
            max_lng=max(lngs)
        )

    def search_fleet_map(self, db: Session, current_user: User, query: str) -> FullFleetMapResponse:
        full_map = self.get_full_fleet_map(db, current_user)
        q = query.lower()
        
        filtered_vehicles = [v for v in full_map.vehicles if q in v.vehicle_name.lower() or q in v.registration_number.lower() or (v.driver_name and q in v.driver_name.lower())]
        filtered_drivers = [d for d in full_map.drivers if q in d.driver_name.lower()]
        filtered_trips = [t for t in full_map.trips if q in str(t.trip_id) or q in t.origin.lower() or q in t.destination.lower()]
        
        bounds = self._calculate_bounds(filtered_vehicles, filtered_drivers)
        
        return FullFleetMapResponse(
            vehicles=filtered_vehicles,
            drivers=filtered_drivers,
            trips=filtered_trips,
            bounds=bounds
        )

    def filter_fleet_map(self, db: Session, current_user: User, vehicle_status: Optional[str] = None, driver_status: Optional[str] = None, trip_status: Optional[str] = None) -> FullFleetMapResponse:
        full_map = self.get_full_fleet_map(db, current_user)
        
        filtered_vehicles = full_map.vehicles
        if vehicle_status:
            filtered_vehicles = [v for v in filtered_vehicles if v.status.lower() == vehicle_status.lower()]
            
        filtered_drivers = full_map.drivers
        if driver_status:
            filtered_drivers = [d for d in filtered_drivers if d.status.lower() == driver_status.lower()]
            
        filtered_trips = full_map.trips
        if trip_status:
            filtered_trips = [t for t in filtered_trips if t.trip_status.lower() == trip_status.lower()]
            
        bounds = self._calculate_bounds(filtered_vehicles, filtered_drivers)
        
        return FullFleetMapResponse(
            vehicles=filtered_vehicles,
            drivers=filtered_drivers,
            trips=filtered_trips,
            bounds=bounds
        )

    def get_bounds(self, db: Session, current_user: User) -> FleetMapBounds:
        full_map = self.get_full_fleet_map(db, current_user)
        return full_map.bounds

fleet_map_service = FleetMapService()
