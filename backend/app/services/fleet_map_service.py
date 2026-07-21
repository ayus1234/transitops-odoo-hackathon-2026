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
    def _apply_rbac_filter_query(self, query: Any, model: Any, current_user: User):
        if not current_user.role:
            return query.filter(model.id == None)  # Return none if no role
        
        role_name = current_user.role.name.lower()
        if role_name == "driver":
            if model == Vehicle:
                # Driver can only see vehicles they are assigned to via active trips
                driver_rec = current_user.driver
                if not driver_rec:
                    return query.filter(model.id == None)
                assigned_vehicle_ids = [t.vehicle_id for t in driver_rec.trips if t.status == 'Dispatched']
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
        vehicles = self._apply_rbac_filter_query(db.query(Vehicle), Vehicle, current_user).all()
        drivers = self._apply_rbac_filter_query(db.query(Driver), Driver, current_user).all()
        trips = self._apply_rbac_filter_query(db.query(Trip).filter(Trip.status == 'Dispatched'), Trip, current_user).all()

        v_markers = []
        for v in vehicles:
            active_trip = db.query(Trip).filter(Trip.vehicle_id == v.id, Trip.status == 'Dispatched').first()
            driver_name = None
            if active_trip:
                driver = db.query(Driver).filter(Driver.id == active_trip.driver_id).first()
                if driver:
                    user = db.query(User).filter(User.id == driver.user_id).first()
                    if user:
                        driver_name = f"{user.first_name} {user.last_name}"
            
            has_critical_alert = db.query(Maintenance).filter(
                Maintenance.vehicle_id == v.id,
                Maintenance.priority == 'Critical',
                Maintenance.status.in_(['Pending', 'Approved', 'In Progress'])
            ).first() is not None
            
            v_markers.append(VehicleMarker(
                vehicle_id=v.id,
                vehicle_name=v.vehicle_name,
                registration_number=v.registration_number,
                latitude=float(v.latitude) if v.latitude else None,
                longitude=float(v.longitude) if v.longitude else None,
                status=v.status,
                driver_name=driver_name,
                active_trip=active_trip.trip_number if active_trip else None,
                has_critical_alert=has_critical_alert,
                last_updated=v.updated_at
            ))

        d_markers = []
        for d in drivers:
            active_trip = db.query(Trip).filter(Trip.driver_id == d.id, Trip.status == 'Dispatched').first()
            assigned_vehicle = None
            if active_trip:
                vehicle = db.query(Vehicle).filter(Vehicle.id == active_trip.vehicle_id).first()
                if vehicle:
                    assigned_vehicle = vehicle.vehicle_name
                    
            user = db.query(User).filter(User.id == d.user_id).first()
            driver_name_str = f"{user.first_name} {user.last_name}" if user else "Unknown Driver"
            
            d_markers.append(DriverMarker(
                driver_id=d.id,
                driver_name=driver_name_str,
                latitude=float(d.latitude) if d.latitude else None,
                longitude=float(d.longitude) if d.longitude else None,
                status=d.status,
                assigned_vehicle=assigned_vehicle,
                active_trip=active_trip.trip_number if active_trip else None,
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
                user_id=current_user.id,
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
