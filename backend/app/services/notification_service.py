from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationCreate
from app.models.notification import Notification
from app.models.user import User

from app.services.activity_service import activity_service
from app.schemas.activity import ActivityCreate
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum


class NotificationService:
    def __init__(self, db: Session):
        self.repository = NotificationRepository(db)

    def create_notification(self, user_id: UUID, notification_in: NotificationCreate) -> Notification:
        notification = self.repository.create(notification_in)
        activity_service.log_activity(
            self.repository.db,
            ActivityCreate(
                module=ModuleEnum.NOTIFICATION,
                activity_type=ActivityTypeEnum.CREATED,
                title="Notification Created",
                description=f"Created notification: {notification.title}",
                user_id=user_id,
                severity=SeverityEnum.INFO
            )
        )
        return notification

    def broadcast_notification(self, db: Session, title: str, description: str, type: str, priority: str, category: str, module_name: str, severity: str = "Info", icon_name: Optional[str] = None, route: Optional[str] = None) -> int:
        from app.models.user import User
        users = db.query(User).filter(User.is_active == True).all()
        
        count = 0
        for user in users:
            notif = NotificationCreate(
                user_id=user.id,
                title=title,
                description=description,
                type=type,
                priority=priority,
                category=category,
                module_name=module_name,
                severity=severity,
                icon_name=icon_name,
                route=route
            )
            created = self.repository.create(notif)
            count += 1
            
            activity_service.log_activity(
                db,
                ActivityCreate(
                    module=ModuleEnum.NOTIFICATION,
                    activity_type=ActivityTypeEnum.CREATED,
                    title="Notification Created",
                    description=f"Broadcast notification: {title}",
                    user_id=user.id,
                    severity=SeverityEnum.INFO
                )
            )
            
        return count

    def get_notification(self, notification_id: UUID, current_user_id: UUID) -> Notification:
        notification = self.repository.get_by_id(notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        if notification.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this notification")
        return notification

    def get_user_notifications(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        priority: Optional[str] = None,
        type: Optional[str] = None,
        category: Optional[str] = None,
        module_name: Optional[str] = None,
        is_read: Optional[bool] = None,
        is_archived: Optional[bool] = False
    ) -> Tuple[int, List[Notification]]:
        
        # RBAC Logic
        user = self.repository.db.query(User).filter(User.id == user_id).first()
        if user and user.role:
            role_name = user.role.name
            if role_name == "Fleet Manager":
                if module_name and module_name not in ["Vehicles", "Drivers", "Trips", "Maintenance", "Fuel"]:
                    return 0, []
            elif role_name == "Finance":
                if module_name and module_name not in ["Expenses", "Reports"]:
                    return 0, []
            elif role_name == "Driver":
                if module_name and module_name not in ["Drivers", "Trips"]:
                    return 0, []

        return self.repository.get_user_notifications(
            user_id=user_id,
            skip=skip,
            limit=limit,
            search=search,
            priority=priority,
            type=type,
            category=category,
            module_name=module_name,
            is_read=is_read,
            is_archived=is_archived
        )

    def mark_read(self, notification_id: UUID, current_user_id: UUID) -> Notification:
        notification = self.get_notification(notification_id, current_user_id)
        if not notification.is_read:
            activity_service.log_activity(
                self.repository.db,
                ActivityCreate(
                    module=ModuleEnum.NOTIFICATION,
                    activity_type=ActivityTypeEnum.UPDATED,
                    title="Notification Read",
                    description=f"Marked read: {notification.title}",
                    user_id=current_user_id,
                    severity=SeverityEnum.INFO
                )
            )
        return self.repository.mark_read(notification.id)

    def mark_unread(self, notification_id: UUID, current_user_id: UUID) -> Notification:
        notification = self.get_notification(notification_id, current_user_id)
        return self.repository.mark_unread(notification.id)

    def mark_all_read(self, current_user_id: UUID) -> int:
        count = self.repository.mark_all_read(current_user_id)
        if count > 0:
            activity_service.log_activity(
                self.repository.db,
                ActivityCreate(
                    module=ModuleEnum.NOTIFICATION,
                    activity_type=ActivityTypeEnum.UPDATED,
                    title="Mark All Read",
                    description=f"Marked {count} notifications as read",
                    user_id=current_user_id,
                    severity=SeverityEnum.INFO
                )
            )
        return count

    def archive(self, notification_id: UUID, current_user_id: UUID) -> Notification:
        notification = self.get_notification(notification_id, current_user_id)
        if not notification.is_archived:
            activity_service.log_activity(
                self.repository.db,
                ActivityCreate(
                    module=ModuleEnum.NOTIFICATION,
                    activity_type=ActivityTypeEnum.UPDATED,
                    title="Notification Archived",
                    description=f"Archived: {notification.title}",
                    user_id=current_user_id,
                    severity=SeverityEnum.INFO
                )
            )
        return self.repository.archive(notification.id)
        
    def unarchive(self, notification_id: UUID, current_user_id: UUID) -> Notification:
        notification = self.get_notification(notification_id, current_user_id)
        return self.repository.unarchive(notification.id)
        
    def execute_notification(self, notification_id: UUID, current_user_id: UUID) -> Dict[str, str]:
        notification = self.mark_read(notification_id, current_user_id)
        activity_service.log_activity(
            self.repository.db,
            ActivityCreate(
                module=ModuleEnum.NOTIFICATION,
                activity_type=ActivityTypeEnum.SYSTEM,
                title="Quick Action Executed",
                description=f"Executed notification: {notification.title}",
                user_id=current_user_id,
                severity=SeverityEnum.INFO
            )
        )
        return {"route": notification.route or "/"}

    def delete(self, notification_id: UUID, current_user_id: UUID) -> bool:
        notification = self.get_notification(notification_id, current_user_id)
        return self.repository.delete(notification.id)

    def get_statistics(self, user_id: UUID) -> Dict[str, Any]:
        return self.repository.get_statistics(user_id)

    @staticmethod
    def notify_user(
        db: Session,
        user_id: UUID,
        title: str,
        description: str,
        type: str,
        priority: str = "Medium",
        category: str = "System",
        module_name: str = "System",
        severity: str = "Info",
        route: Optional[str] = None,
        icon_name: Optional[str] = None,
        metadata_payload: Optional[Dict[str, Any]] = None
    ) -> Notification:
        repo = NotificationRepository(db)
        notif = NotificationCreate(
            user_id=user_id,
            title=title,
            description=description,
            type=type,
            priority=priority,
            category=category,
            module_name=module_name,
            severity=severity,
            route=route,
            icon_name=icon_name,
            metadata_payload=metadata_payload
        )
        return repo.create(notif)
