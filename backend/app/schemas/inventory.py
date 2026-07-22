from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Any, Dict
from datetime import datetime
from uuid import UUID

from app.models.inventory import (
    PartStatusEnum, 
    ProcurementStatusEnum, 
    PriorityEnum, 
    ShipmentStatusEnum, 
    InventoryHistoryTypeEnum
)

# --- Inventory Item Schemas ---

class InventoryItemBase(BaseModel):
    name: str = Field(..., description="Name of the part")
    part_number: str = Field(..., description="Unique part number")
    description: Optional[str] = None
    quantity_available: int = Field(0, description="Available quantity in stock")
    quantity_reserved: int = Field(0, description="Quantity reserved for maintenance")
    minimum_stock_level: int = Field(5, description="Level at which low stock warning triggers")
    critical_stock_level: int = Field(2, description="Level at which critical stock warning triggers")
    unit_cost: float = Field(0.0, description="Cost per unit")
    location: Optional[str] = None
    vendor: Optional[str] = None
    status: PartStatusEnum = PartStatusEnum.IN_STOCK

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    part_number: Optional[str] = None
    description: Optional[str] = None
    quantity_available: Optional[int] = None
    quantity_reserved: Optional[int] = None
    minimum_stock_level: Optional[int] = None
    critical_stock_level: Optional[int] = None
    unit_cost: Optional[float] = None
    location: Optional[str] = None
    vendor: Optional[str] = None
    status: Optional[PartStatusEnum] = None

class InventoryItemResponse(InventoryItemBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# --- Procurement Request Schemas ---

class ProcurementRequestBase(BaseModel):
    part_id: UUID
    required_quantity: int
    suggested_quantity: Optional[int] = None
    vendor: Optional[str] = None
    estimated_cost: Optional[float] = None
    priority: PriorityEnum = PriorityEnum.MEDIUM

class ProcurementRequestCreate(ProcurementRequestBase):
    pass

class ProcurementRequestUpdate(BaseModel):
    part_id: Optional[UUID] = None
    required_quantity: Optional[int] = None
    suggested_quantity: Optional[int] = None
    vendor: Optional[str] = None
    estimated_cost: Optional[float] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[ProcurementStatusEnum] = None

class ProcurementRequestResponse(ProcurementRequestBase):
    id: UUID
    procurement_id: str
    requested_by_id: Optional[UUID] = None
    approved_by_id: Optional[UUID] = None
    status: ProcurementStatusEnum
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # We can include a simplified part object if needed, handled in router
    part: Optional[InventoryItemResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

# --- Purchase Order Schemas ---

class PurchaseOrderBase(BaseModel):
    procurement_request_id: UUID
    vendor_name: str
    quantity: int
    cost: float
    delivery_date: Optional[datetime] = None
    tracking_id: Optional[str] = None

class PurchaseOrderCreate(PurchaseOrderBase):
    pass

class PurchaseOrderUpdate(BaseModel):
    vendor_name: Optional[str] = None
    quantity: Optional[int] = None
    cost: Optional[float] = None
    delivery_date: Optional[datetime] = None
    tracking_id: Optional[str] = None
    shipment_status: Optional[ShipmentStatusEnum] = None

class PurchaseOrderResponse(PurchaseOrderBase):
    id: UUID
    po_number: str
    order_date: datetime
    shipment_status: ShipmentStatusEnum
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# --- Inventory History Schemas ---

class InventoryHistoryBase(BaseModel):
    part_id: UUID
    type: InventoryHistoryTypeEnum
    quantity_changed: int
    previous_quantity: int
    new_quantity: int
    vendor: Optional[str] = None
    cost: Optional[float] = None
    reference_id: Optional[str] = None

class InventoryHistoryCreate(InventoryHistoryBase):
    user_id: Optional[UUID] = None

class InventoryHistoryResponse(InventoryHistoryBase):
    id: UUID
    user_id: Optional[UUID] = None
    created_at: datetime
    
    part: Optional[InventoryItemResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

class InventoryAdjustmentRequest(BaseModel):
    quantity_change: int
    type: InventoryHistoryTypeEnum
    reference_id: Optional[str] = None
    vendor: Optional[str] = None
    cost: Optional[float] = None

# --- Summary & Dashboard Schemas ---

class InventoryDashboardSummary(BaseModel):
    total_parts: int
    available_parts: int
    low_stock_parts: int
    critical_stock_alerts: int
    out_of_stock_parts: int
    vehicles_waiting: int
    estimated_downtime_hours: float
    pending_procurement_requests: int
    pending_purchase_orders: int
    inventory_health_score: float

class ProcurementSummary(BaseModel):
    total_requests: int
    draft_requests: int
    submitted_requests: int
    approved_requests: int
    rejected_requests: int
    ordered_requests: int
    delivered_requests: int

class PurchaseOrderSummary(BaseModel):
    total_orders: int
    processing: int
    ordered: int
    dispatched: int
    in_transit: int
    delivered: int
    delayed: int
