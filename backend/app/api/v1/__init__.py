"""
API v1 routes package.
"""
from fastapi import APIRouter

from app.api.v1 import auth, vehicles, drivers, trips, maintenance, maintenance_technicians, maintenance_tasks, fuel, expenses, dashboard, reports, admin, notifications, help_center, quick_actions, custom_reports, activity, fleet_map, license_compliance, fleet_compliance, safety_insights, inventory, procurement, purchase_orders, rbac

# Create main API router
api_router = APIRouter()

# Include route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
api_router.include_router(drivers.router, prefix="/drivers", tags=["Drivers"])
api_router.include_router(trips.router, prefix="/trips", tags=["Trips"])
api_router.include_router(maintenance_technicians.router, prefix="/maintenance/technicians", tags=["Technician Management"])
api_router.include_router(maintenance_tasks.router, prefix="/maintenance/tasks", tags=["Maintenance Tasks"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["Maintenance"])
api_router.include_router(fuel.router, prefix="/fuel", tags=["Fuel"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(help_center.router, prefix="/help", tags=["Help Center"])
api_router.include_router(quick_actions.router, prefix="/quick-actions", tags=["Quick Actions"])
api_router.include_router(custom_reports.router, prefix="/custom-reports", tags=["Custom Reports"])
api_router.include_router(activity.router, prefix="/activity", tags=["Activity"])
api_router.include_router(fleet_map.router, prefix="/fleet-map", tags=["Fleet Map"])
api_router.include_router(license_compliance.router, prefix="/license-compliance", tags=["License Compliance"])
api_router.include_router(fleet_compliance.router, prefix="/fleet-compliance", tags=["Fleet Compliance"])
api_router.include_router(safety_insights.router, prefix="/safety-insights", tags=["Safety Insights"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(procurement.router, prefix="/procurement", tags=["Procurement"])
api_router.include_router(purchase_orders.router, prefix="/purchase-orders", tags=["Purchase Orders"])
api_router.include_router(rbac.router, prefix="/settings", tags=["Settings & Permissions"])
