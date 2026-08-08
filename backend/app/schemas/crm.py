"""
Logistics CRM & Client Account Pydantic Schemas.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class ClientAccount(BaseModel):
    """Logistics client customer profile."""
    client_id: UUID
    company_name: str
    contact_person: str
    email: str
    phone: str
    credit_limit_usd: float
    contract_tier: str  # "Enterprise", "Standard", "VIP"
    rate_per_km_usd: float
    total_jobs_booked: int
    total_revenue_usd: float


class ClientBookingRequest(BaseModel):
    """Client load booking request."""
    client_id: UUID
    origin: str
    destination: str
    cargo_weight_kg: float
    required_delivery_by: datetime
    notes: Optional[str] = None
