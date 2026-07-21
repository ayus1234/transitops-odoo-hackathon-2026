from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.fleet_map import FullFleetMapResponse, VehicleMarker, DriverMarker, TripMarker, FleetMapBounds
from app.services.fleet_map_service import fleet_map_service

router = APIRouter()

@router.get("/full", response_model=FullFleetMapResponse)
def get_full_fleet_map(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return fleet_map_service.get_full_fleet_map(db, current_user)

@router.get("/vehicles", response_model=List[VehicleMarker])
def get_vehicle_markers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return fleet_map_service.get_full_fleet_map(db, current_user).vehicles

@router.get("/drivers", response_model=List[DriverMarker])
def get_driver_markers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return fleet_map_service.get_full_fleet_map(db, current_user).drivers

@router.get("/trips", response_model=List[TripMarker])
def get_active_trips(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return fleet_map_service.get_full_fleet_map(db, current_user).trips

@router.get("/search", response_model=FullFleetMapResponse)
def search_fleet_map(q: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return fleet_map_service.search_fleet_map(db, current_user, q)

@router.get("/filter", response_model=FullFleetMapResponse)
def filter_fleet_map(
    vehicle_status: Optional[str] = None,
    driver_status: Optional[str] = None,
    trip_status: Optional[str] = None,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return fleet_map_service.filter_fleet_map(db, current_user, vehicle_status, driver_status, trip_status)

@router.get("/bounds", response_model=FleetMapBounds)
def get_bounds(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return fleet_map_service.get_bounds(db, current_user)
