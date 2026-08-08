"""
AI Fleet Copilot Pydantic Schemas.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AICopilotQueryRequest(BaseModel):
    """User query to AI Fleet Copilot."""
    prompt: str = Field(..., min_length=2)
    context_vehicle_id: Optional[str] = None
    context_trip_id: Optional[str] = None


class AICopilotQueryResponse(BaseModel):
    """AI Copilot response payload with structured data and suggested actions."""
    answer: str
    intent: str  # "FLEET_HEALTH", "RECOMMENDATION", "FUEL_CHECK", "PAYROLL", "GENERAL"
    structured_data: Optional[Dict[str, Any]] = None
    suggested_actions: List[Dict[str, str]] = []
