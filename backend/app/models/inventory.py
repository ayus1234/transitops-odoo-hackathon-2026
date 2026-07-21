from sqlalchemy import Column, String, ForeignKey, DateTime, func, Integer, Float, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base

class PartStatusEnum(str, enum.Enum):
    IN_STOCK = "In Stock"
    LOW_STOCK = "Low Stock"
    CRITICAL_STOCK = "Critical Stock"
    OUT_OF_STOCK = "Out Of Stock"
    RESERVED = "Reserved"
    INCOMING_SHIPMENT = "Incoming Shipment"

class ProcurementStatusEnum(str, enum.Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    ORDERED = "Ordered"
    DELIVERED = "Delivered"

class PriorityEnum(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class ShipmentStatusEnum(str, enum.Enum):
    PROCESSING = "Processing"
    ORDERED = "Ordered"
    PACKED = "Packed"
    DISPATCHED = "Dispatched"
    IN_TRANSIT = "In Transit"
    DELIVERED = "Delivered"
    DELAYED = "Delayed"

class InventoryHistoryTypeEnum(str, enum.Enum):
    RESTOCK = "Restock"
    RELEASE = "Release"
    ADJUSTMENT = "Adjustment"
    RESERVED = "Reserved"

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    part_number = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    quantity_available = Column(Integer, default=0, nullable=False)
    quantity_reserved = Column(Integer, default=0, nullable=False)
    minimum_stock_level = Column(Integer, default=5, nullable=False)
    critical_stock_level = Column(Integer, default=2, nullable=False)
    
    unit_cost = Column(Float, default=0.0, nullable=False)
    location = Column(String, nullable=True) # e.g. "Aisle 4, Bin B"
    vendor = Column(String, nullable=True)
    
    status = Column(Enum(PartStatusEnum), default=PartStatusEnum.IN_STOCK, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    procurement_requests = relationship("ProcurementRequest", back_populates="part", cascade="all, delete-orphan")
    history_logs = relationship("InventoryHistory", back_populates="part", cascade="all, delete-orphan")

class ProcurementRequest(Base):
    __tablename__ = "procurement_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    procurement_id = Column(String, unique=True, nullable=False) # e.g. "PR-2023-001"
    
    part_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False)
    requested_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    required_quantity = Column(Integer, nullable=False)
    suggested_quantity = Column(Integer, nullable=True)
    
    vendor = Column(String, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.MEDIUM, nullable=False)
    status = Column(Enum(ProcurementStatusEnum), default=ProcurementStatusEnum.DRAFT, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    part = relationship("InventoryItem", back_populates="procurement_requests")
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    purchase_orders = relationship("PurchaseOrder", back_populates="procurement_request", cascade="all, delete-orphan")

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    po_number = Column(String, unique=True, nullable=False)
    procurement_request_id = Column(UUID(as_uuid=True), ForeignKey("procurement_requests.id", ondelete="CASCADE"), nullable=False)
    
    vendor_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    delivery_date = Column(DateTime(timezone=True), nullable=True)
    
    tracking_id = Column(String, nullable=True)
    shipment_status = Column(Enum(ShipmentStatusEnum), default=ShipmentStatusEnum.PROCESSING, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    procurement_request = relationship("ProcurementRequest", back_populates="purchase_orders")

class InventoryHistory(Base):
    __tablename__ = "inventory_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    part_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False)
    
    type = Column(Enum(InventoryHistoryTypeEnum), nullable=False)
    
    quantity_changed = Column(Integer, nullable=False)
    previous_quantity = Column(Integer, nullable=False)
    new_quantity = Column(Integer, nullable=False)
    
    vendor = Column(String, nullable=True)
    cost = Column(Float, nullable=True)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reference_id = Column(String, nullable=True) # e.g. PO Number or Maintenance Log ID
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    part = relationship("InventoryItem", back_populates="history_logs")
    user = relationship("User")
