"""
API v1 routes package.
"""
from fastapi import APIRouter

from app.api.v1 import auth, vehicles, drivers

# Create main API router
api_router = APIRouter()

# Include route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
api_router.include_router(drivers.router, prefix="/drivers", tags=["Drivers"])

# Future routes will be added here:
# api_router.include_router(trips.router, prefix="/trips", tags=["Trips"])
