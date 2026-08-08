"""
Schemas for Vehicle & Driver Recommendation Engine.
"""
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class MatchScoreBreakdown(BaseModel):
    """Detailed score breakdown per ranking dimension (0 to 100)."""
    capacity_score: float = Field(..., ge=0.0, le=100.0, description="Payload capacity fit score")
    proximity_score: float = Field(..., ge=0.0, le=100.0, description="Location proximity score")
    health_score: float = Field(..., ge=0.0, le=100.0, description="Fleet health & compliance score")
    driver_score: float = Field(..., ge=0.0, le=100.0, description="Driver availability & suitability score")


class VehicleRecommendationItem(BaseModel):
    """Ranked vehicle recommendation item."""
    model_config = ConfigDict(from_attributes=True)

    vehicle_id: UUID
    vehicle_name: str
    registration_number: str
    vehicle_type: str
    capacity_kg: float
    current_status: str
    overall_match_score: float = Field(..., ge=0.0, le=100.0)
    score_breakdown: MatchScoreBreakdown
    match_reasons: List[str]
    suggested_driver_id: Optional[UUID] = None
    suggested_driver_name: Optional[str] = None
    estimated_proximity_km: Optional[float] = None


class VehicleRecommendationResponse(BaseModel):
    """Response payload for job vehicle recommendations."""
    job_id: UUID
    job_number: str
    cargo_weight_kg: float
    total_candidates_evaluated: int
    recommendations: List[VehicleRecommendationItem]
