from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date

# ----------------------------------------------------
# 1. License Compliance Schemas
# ----------------------------------------------------
class LicenseSummary(BaseModel):
    total_drivers: int
    valid_licenses: int
    expired_licenses: int
    expiring_in_7_days: int
    expiring_in_30_days: int
    compliance_percentage: float

class DriverLicenseInfo(BaseModel):
    id: UUID
    full_name: str
    license_number: str
    license_category: str
    license_expiry_date: date
    status: str # Valid, Expiring Soon, Expired, Suspended
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedLicenseResponse(BaseModel):
    data: List[DriverLicenseInfo]
    pagination: dict
    success: bool = True

# ----------------------------------------------------
# 2. Fleet Compliance Schemas
# ----------------------------------------------------
class FleetComplianceSummary(BaseModel):
    fleet_compliance_score: float
    driver_compliance_score: float
    vehicle_compliance_score: float
    maintenance_compliance_score: float
    inspection_compliance_score: float

class TrendDataPoint(BaseModel):
    label: str
    value: float

class FleetComplianceAnalytics(BaseModel):
    weekly_trends: List[TrendDataPoint]
    monthly_trends: List[TrendDataPoint]
    
class ExportResponse(BaseModel):
    success: bool = True
    url: str

# ----------------------------------------------------
# 3. Safety Insights Schemas
# ----------------------------------------------------
class SafetySummary(BaseModel):
    fleet_safety_score: float
    excellent_count: int
    good_count: int
    average_count: int
    needs_attention_count: int

class DriverSafetyInfo(BaseModel):
    id: UUID
    full_name: str
    safety_score: float
    rank: int
    performance: str # Excellent, Good, Average, Needs Attention

    model_config = ConfigDict(from_attributes=True)

class SafetyAlert(BaseModel):
    id: str # UUID or string
    driver_name: str
    vehicle_name: str
    alert_type: str
    severity: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UnsafeDrivingStat(BaseModel):
    metric: str
    count: int

class SafetyAnalytics(BaseModel):
    weekly_trends: List[TrendDataPoint]
    monthly_trends: List[TrendDataPoint]
    unsafe_driving_statistics: List[UnsafeDrivingStat]
