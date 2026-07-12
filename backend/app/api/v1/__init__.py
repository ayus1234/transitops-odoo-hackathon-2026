"""
API v1 routes package.
"""
from fastapi import APIRouter

from app.api.v1 import auth

# Create main API router
api_router = APIRouter()

# Include route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Future routes will be added here:
# api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
# api_router.include_router(drivers.router, prefix="/drivers", tags=["Drivers"])
# api_router.include_router(trips.router, prefix="/trips", tags=["Trips"])
