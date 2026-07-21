from sqlalchemy import Column, String, ForeignKey, DateTime, func, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base

JSONVariant = JSON().with_variant(JSONB, 'postgresql')

class ModuleEnum(str, enum.Enum):
    AUTHENTICATION = "Authentication"
    DASHBOARD = "Dashboard"
    VEHICLE = "Vehicle"
    DRIVER = "Driver"
    TRIP = "Trip"
    MAINTENANCE = "Maintenance"
    FUEL = "Fuel"
    EXPENSE = "Expense"
    REPORTS = "Reports"
    SETTINGS = "Settings"
    NOTIFICATION = "Notification"
    HELP_CENTER = "Help Center"
    QUICK_ACTIONS = "Quick Actions"
    CUSTOM_REPORTS = "Custom Reports"
    INVENTORY = "Inventory"
    PROCUREMENT = "Procurement"
    PURCHASE_ORDER = "Purchase Order"

class ActivityTypeEnum(str, enum.Enum):
    CREATED = "Created"
    UPDATED = "Updated"
    DELETED = "Deleted"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    ASSIGNED = "Assigned"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    EXPORTED = "Exported"
    LOGIN = "Login"
    LOGOUT = "Logout"
    PASSWORD_RESET = "Password Reset"
    NOTIFICATION = "Notification"
    SYSTEM = "System"

class SeverityEnum(str, enum.Enum):
    INFO = "Info"
    SUCCESS = "Success"
    WARNING = "Warning"
    CRITICAL = "Critical"

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Optional relation to various main entities
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="SET NULL"), nullable=True)
    maintenance_id = Column(UUID(as_uuid=True), ForeignKey("maintenance_logs.id", ondelete="SET NULL"), nullable=True)
    fuel_id = Column(UUID(as_uuid=True), ForeignKey("fuel_logs.id", ondelete="SET NULL"), nullable=True)
    expense_id = Column(UUID(as_uuid=True), ForeignKey("expenses.id", ondelete="SET NULL"), nullable=True)

    module = Column(Enum(ModuleEnum), nullable=False)
    activity_type = Column(Enum(ActivityTypeEnum), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    severity = Column(Enum(SeverityEnum), nullable=False, default=SeverityEnum.INFO)
    status = Column(String, nullable=True) # E.g., 'Success', 'Failed'
    
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    details = Column("metadata", JSONVariant, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships (Optional based on performance needs, usually good for back_populates if needed, but not strictly required here if it's just a log)
    user = relationship("User", foreign_keys=[user_id])
