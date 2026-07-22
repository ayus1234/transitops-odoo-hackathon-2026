"""
SQLAlchemy models package.
"""
from app.core.database import Base
from app.models.role import Role, user_additional_roles
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.trip import Trip
from app.models.maintenance import Maintenance
from app.models.fuel import Fuel
from app.models.expense import Expense
from app.models.permission import Permission
from app.models.settings import ApplicationSettings, OrganizationSettings
from app.models.notification import Notification
from app.models.help_center import HelpCategory, HelpArticle, SupportTicket, Feedback
from app.models.quick_action import QuickAction, UserFavoriteAction, UserRecentAction
from app.models.custom_report import CustomReport, ReportExecution, ScheduledReport
from app.models.activity import ActivityLog
from app.models.permission_audit import PermissionAuditLog
from app.models.inventory import InventoryItem, ProcurementRequest, PurchaseOrder, InventoryHistory

__all__ = [
    "Base", "Role", "user_additional_roles", "User", "Vehicle", "Driver", "Trip",
    "Maintenance", "Fuel", "Expense", "Permission",
    "ApplicationSettings", "OrganizationSettings", "Notification",
    "HelpCategory", "HelpArticle", "SupportTicket", "Feedback",
    "QuickAction", "UserFavoriteAction", "UserRecentAction",
    "CustomReport", "ReportExecution", "ScheduledReport",
    "ActivityLog", "PermissionAuditLog",
    "InventoryItem", "ProcurementRequest", "PurchaseOrder", "InventoryHistory"
]
