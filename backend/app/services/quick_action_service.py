"""
Quick Actions service layer for business logic and RBAC filtering.
"""
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.quick_action_repository import QuickActionRepository
from app.models.user import User
from app.models.quick_action import QuickAction
from app.schemas.quick_action import QuickActionResponse
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.services.activity_service import activity_service
from app.schemas.activity import ActivityCreate
from app.services.notification_service import NotificationService
from app.schemas.notification import NotificationCreate
from datetime import datetime
import csv
import json
import io


class QuickActionService:
    """Service for managing Quick Actions and handling permissions."""
    
    def __init__(self, db: Session):
        self.repository = QuickActionRepository(db)
        
    def _apply_permissions_and_favorites(self, actions: List[QuickAction], user: User) -> List[Dict]:
        """
        Filter actions based on user's RBAC permissions and attach the dynamic
        is_favorite flag for the current user.
        """
        # Fetch all user favorites once to avoid N+1 queries
        user_favorites = set(self.repository.get_user_favorites(user.id))
        
        filtered_actions = []
        for action in actions:
            # RBAC Check: ensure user has the required permission for this specific action route
            if user.has_permission(action.permission_resource, action.permission_action):
                # We convert the SQLAlchemy model to a dict, because we need to override `is_favorite`
                # which might be defined globally on the model, but we want it per-user
                action_dict = {
                    "id": action.id,
                    "name": action.name,
                    "display_name": action.display_name,
                    "description": action.description,
                    "icon": action.icon,
                    "category": action.category,
                    "route": action.route,
                    "http_method": action.http_method,
                    "permission_resource": action.permission_resource,
                    "permission_action": action.permission_action,
                    "display_order": action.display_order,
                    "color": action.color,
                    "is_active": action.is_active,
                    "created_at": action.created_at,
                    "updated_at": action.updated_at,
                    "is_favorite": action.id in user_favorites
                }
                filtered_actions.append(action_dict)
                
        # Sort so favorites appear first, then by display order
        filtered_actions.sort(key=lambda x: (not x["is_favorite"], x["display_order"], x["display_name"]))
        return filtered_actions

    def get_available_actions(self, user: User) -> List[Dict]:
        """Get all active actions the user is authorized to perform."""
        all_active = self.repository.list_active_actions()
        return self._apply_permissions_and_favorites(all_active, user)
        
    def get_favorite_actions(self, user: User) -> List[Dict]:
        """Get all favorite actions for the user."""
        all_active = self.repository.list_active_actions()
        authorized_actions = self._apply_permissions_and_favorites(all_active, user)
        return [a for a in authorized_actions if a["is_favorite"]]
        
    def get_recent_actions(self, user: User, limit: int = 10) -> List[Dict]:
        """Get recently executed actions for the user."""
        recent_records = self.repository.get_user_recent_actions(user.id, limit)
        user_favorites = set(self.repository.get_user_favorites(user.id))
        
        result = []
        for record in recent_records:
            action = record.action
            if user.has_permission(action.permission_resource, action.permission_action):
                # Construct RecentActionResponse shape manually
                action_dict = {
                    "id": action.id,
                    "name": action.name,
                    "display_name": action.display_name,
                    "description": action.description,
                    "icon": action.icon,
                    "category": action.category,
                    "route": action.route,
                    "http_method": action.http_method,
                    "permission_resource": action.permission_resource,
                    "permission_action": action.permission_action,
                    "display_order": action.display_order,
                    "color": action.color,
                    "is_active": action.is_active,
                    "created_at": action.created_at,
                    "updated_at": action.updated_at,
                    "is_favorite": action.id in user_favorites
                }
                result.append({
                    "id": record.id,
                    "action_id": record.action_id,
                    "last_accessed_at": record.last_accessed_at,
                    "access_count": record.access_count,
                    "action": action_dict
                })
                
        return result
        
    def search_actions(self, user: User, keyword: Optional[str] = None, category: Optional[str] = None) -> List[Dict]:
        """Search actions by keyword or category, filtered by permissions."""
        actions = self.repository.search_actions(keyword, category)
        return self._apply_permissions_and_favorites(actions, user)
        
    def toggle_favorite(self, action_id: UUID, is_favorite: bool, user: User) -> Dict:
        """Toggle favorite status of an action."""
        action = self.repository.get_action(action_id)
        if not action or not action.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")
            
        if not user.has_permission(action.permission_resource, action.permission_action):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to favorite this action")
            
        new_status = self.repository.toggle_favorite(user.id, action_id, is_favorite)
        
        action_dict = {
            "id": action.id,
            "name": action.name,
            "display_name": action.display_name,
            "description": action.description,
            "icon": action.icon,
            "category": action.category,
            "route": action.route,
            "http_method": action.http_method,
            "permission_resource": action.permission_resource,
            "permission_action": action.permission_action,
            "display_order": action.display_order,
            "color": action.color,
            "is_active": action.is_active,
            "created_at": action.created_at,
            "updated_at": action.updated_at,
            "is_favorite": new_status
        }
        
        # Log to activity engine
        action_verb = "Added to" if new_status else "Removed from"
        act_log = ActivityCreate(
            module=ModuleEnum.QUICK_ACTIONS,
            activity_type=ActivityTypeEnum.UPDATED,
            title=f"Quick Action {action_verb} Favorites",
            description=f"Action '{action.display_name}' was {action_verb.lower()} favorites.",
            severity=SeverityEnum.INFO,
            status="Success",
            user_id=user.id
        )
        activity_service.log_activity(self.repository.db, act_log)
        
        return action_dict
        
    def execute_action(self, action_id: UUID, user: User) -> Dict:
        """Log the execution and return action details."""
        action = self.repository.get_action(action_id)
        if not action or not action.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found")
            
        if not user.has_permission(action.permission_resource, action.permission_action):
            # Permission Denied Logic
            notification_svc = NotificationService(self.repository.db)
            notification_svc.notify_user(
                db=self.repository.db,
                user_id=user.id,
                title="Permission Denied",
                description=f"You do not have permission to execute '{action.display_name}'.",
                type="Warning",
                priority="High",
                category="System",
                module_name="Quick Actions",
                severity="Warning",
                icon_name="block"
            )
            
            activity_service.log_activity(self.repository.db, ActivityCreate(
                module=ModuleEnum.QUICK_ACTIONS,
                activity_type=ActivityTypeEnum.SYSTEM,
                title="Permission Denied",
                description=f"Attempted to execute '{action.display_name}' without proper permissions.",
                severity=SeverityEnum.WARNING,
                status="Failed",
                user_id=user.id
            ))
            
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to execute this action")
            
        self.repository.log_execution(user.id, action.id)
        
        # Determine if it's a favorite
        user_favorites = set(self.repository.get_user_favorites(user.id))
        
        action_dict = {
            "id": action.id,
            "name": action.name,
            "display_name": action.display_name,
            "description": action.description,
            "icon": action.icon,
            "category": action.category,
            "route": action.route,
            "http_method": action.http_method,
            "permission_resource": action.permission_resource,
            "permission_action": action.permission_action,
            "display_order": action.display_order,
            "color": action.color,
            "is_active": action.is_active,
            "created_at": action.created_at,
            "updated_at": action.updated_at,
            "is_favorite": action.id in user_favorites
        }
        
        # Map action name to specific activity and notification messages
        activity_title = "Quick Action Executed"
        activity_desc = f"Executed quick action: {action.display_name}"
        notif_title = None
        notif_desc = None
        
        if action.name == "register_vehicle":
            activity_title = "Vehicle Registration Started"
            activity_desc = "Initiated the vehicle registration workflow."
            notif_title = "Vehicle Registered"
            notif_desc = "Vehicle registration workflow was initiated."
        elif action.name == "create_trip":
            activity_title = "Trip Wizard Opened"
            activity_desc = "Initiated the trip creation wizard."
            notif_title = "Trip Created"
            notif_desc = "Trip creation wizard was initiated."
        elif action.name == "assign_driver":
            activity_title = "Driver Assignment Started"
            activity_desc = "Initiated the driver assignment workflow."
            notif_title = "Driver Assigned"
            notif_desc = "Driver assignment workflow was initiated."
        elif action.name in ["generate_report", "create_custom_report"]:
            activity_title = "Report Builder Opened"
            activity_desc = "Initiated the custom report builder."
            notif_title = "Report Generated"
            notif_desc = "Custom report builder was initiated."

        # Log execution to Activity Tracking Engine
        act_log = ActivityCreate(
            module=ModuleEnum.QUICK_ACTIONS,
            activity_type=ActivityTypeEnum.SYSTEM,
            title=activity_title,
            description=activity_desc,
            severity=SeverityEnum.INFO,
            status="Success",
            user_id=user.id
        )
        activity_service.log_activity(self.repository.db, act_log)
        
        # Generate Notification if applicable
        if notif_title:
            notification_svc = NotificationService(self.repository.db)
            notification_svc.notify_user(
                db=self.repository.db,
                user_id=user.id,
                title=notif_title,
                description=notif_desc,
                type="Info",
                priority="Medium",
                category="System",
                module_name="Quick Actions",
                severity="Info",
                icon_name=action.icon
            )
        
        return {
            "action": action_dict,
            "target_route": action.route,
            "http_method": action.http_method or "GET",
            "required_permission": {
                "resource": action.permission_resource,
                "action": action.permission_action
            }
        }
        
    def get_statistics(self, user: User) -> Dict[str, Any]:
        """Get statistics for Quick Actions."""
        return self.repository.get_statistics(user.id)

    def get_permissions(self, user: User) -> Dict[str, List[Dict]]:
        """Get allowed and restricted actions based on user's RBAC."""
        all_active = self.repository.list_active_actions()
        allowed = []
        restricted = []
        
        user_favorites = set(self.repository.get_user_favorites(user.id))
        
        for action in all_active:
            action_dict = {
                "id": action.id,
                "name": action.name,
                "display_name": action.display_name,
                "description": action.description,
                "icon": action.icon,
                "category": action.category,
                "route": action.route,
                "http_method": action.http_method,
                "permission_resource": action.permission_resource,
                "permission_action": action.permission_action,
                "display_order": action.display_order,
                "color": action.color,
                "is_active": action.is_active,
                "created_at": action.created_at,
                "updated_at": action.updated_at,
                "is_favorite": action.id in user_favorites
            }
            if user.has_permission(action.permission_resource, action.permission_action):
                allowed.append(action_dict)
            else:
                restricted.append(action_dict)
                
        # Sort them
        allowed.sort(key=lambda x: (not x["is_favorite"], x["display_order"], x["display_name"]))
        restricted.sort(key=lambda x: (x["display_order"], x["display_name"]))
        
        return {
            "allowed": allowed,
            "restricted": restricted
        }
        
    def add_favorite(self, action_id: UUID, user: User) -> Dict:
        """Explicitly add a favorite."""
        return self.toggle_favorite(action_id, True, user)
        
    def remove_favorite(self, action_id: UUID, user: User) -> Dict:
        """Explicitly remove a favorite."""
        return self.toggle_favorite(action_id, False, user)

    def export_data(self, user: User, format: str, export_type: str) -> Tuple[str, bytes, str]:
        """Export Recent, Favorites, or Statistics to CSV, JSON, or PDF."""
        data = []
        filename = f"quick_actions_{export_type}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        if export_type == "recent":
            records = self.get_recent_actions(user, limit=50)
            data = [{"Action": r["action"]["display_name"], "Accessed At": str(r["last_accessed_at"]), "Count": r["access_count"]} for r in records]
        elif export_type == "favorites":
            records = self.get_favorite_actions(user)
            data = [{"Action": r["display_name"], "Category": r["category"], "Route": r["route"]} for r in records]
        elif export_type == "statistics":
            stats = self.get_statistics(user)
            data = [{"Metric": k, "Value": v} for k, v in stats.items()]
        else:
            raise HTTPException(status_code=400, detail="Invalid export type")
            
        if format == "json":
            content = json.dumps(data, indent=2).encode('utf-8')
            return f"{filename}.json", content, "application/json"
        elif format == "csv":
            output = io.StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            content = output.getvalue().encode('utf-8')
            return f"{filename}.csv", content, "text/csv"
        elif format == "pdf":
            # Simulate PDF export by returning a structured text file or simple PDF byte stream placeholder
            content = f"PDF Export for {export_type}\n\n".encode('utf-8')
            for row in data:
                content += str(row).encode('utf-8') + b"\n"
            return f"{filename}.pdf", content, "application/pdf"
        else:
            raise HTTPException(status_code=400, detail="Invalid export format")
