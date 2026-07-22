from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, notification_in: NotificationCreate) -> Notification:
        db_notification = Notification(
            user_id=notification_in.user_id,
            title=notification_in.title,
            description=notification_in.description,
            type=notification_in.type,
            priority=notification_in.priority,
            category=notification_in.category,
            module_name=notification_in.module_name,
            severity=notification_in.severity,
            icon_name=notification_in.icon_name,
            route=notification_in.route,
            related_entity_id=notification_in.related_entity_id,
            metadata_payload=notification_in.metadata_payload
        )
        self.db.add(db_notification)
        self.db.commit()
        self.db.refresh(db_notification)
        return db_notification

    def get_by_id(self, notification_id: UUID) -> Optional[Notification]:
        stmt = select(Notification).where(Notification.id == notification_id)
        return self.db.execute(stmt).scalar_one_or_none()

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
        
        stmt = select(Notification).where(Notification.user_id == user_id)
        
        if is_archived is not None:
            stmt = stmt.where(Notification.is_archived == is_archived)
            
        if is_read is not None:
            stmt = stmt.where(Notification.is_read == is_read)
            
        if priority:
            stmt = stmt.where(Notification.priority == priority)
            
        if type:
            stmt = stmt.where(Notification.type == type)
            
        if category:
            stmt = stmt.where(Notification.category == category)
            
        if module_name:
            stmt = stmt.where(Notification.module_name == module_name)
            
        if search:
            search_filter = f"%{search}%"
            stmt = stmt.where(
                Notification.title.ilike(search_filter) | 
                Notification.description.ilike(search_filter) |
                Notification.category.ilike(search_filter) |
                Notification.module_name.ilike(search_filter)
            )

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        # Get paginated data
        stmt = stmt.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        notifications = self.db.execute(stmt).scalars().all()
        
        return total, list(notifications)

    def mark_read(self, notification_id: UUID) -> Optional[Notification]:
        notification = self.get_by_id(notification_id)
        if notification:
            notification.is_read = True
            self.db.commit()
            self.db.refresh(notification)
        return notification

    def mark_unread(self, notification_id: UUID) -> Optional[Notification]:
        notification = self.get_by_id(notification_id)
        if notification:
            notification.is_read = False
            self.db.commit()
            self.db.refresh(notification)
        return notification

    def mark_all_read(self, user_id: UUID) -> int:
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount

    def archive(self, notification_id: UUID) -> Optional[Notification]:
        notification = self.get_by_id(notification_id)
        if notification:
            notification.is_archived = True
            self.db.commit()
            self.db.refresh(notification)
        return notification

    def unarchive(self, notification_id: UUID) -> Optional[Notification]:
        notification = self.get_by_id(notification_id)
        if notification:
            notification.is_archived = False
            self.db.commit()
            self.db.refresh(notification)
        return notification

    def delete(self, notification_id: UUID) -> bool:
        stmt = delete(Notification).where(Notification.id == notification_id)
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0

    def get_statistics(self, user_id: UUID) -> Dict[str, Any]:
        # Total
        total_stmt = select(func.count(Notification.id)).where(Notification.user_id == user_id)
        total = self.db.execute(total_stmt).scalar_one()

        # Unread
        unread_stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id, Notification.is_read == False, Notification.is_archived == False
        )
        unread = self.db.execute(unread_stmt).scalar_one()

        # Read (not archived)
        read_stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id, Notification.is_read == True, Notification.is_archived == False
        )
        read = self.db.execute(read_stmt).scalar_one()

        # Archived
        archived_stmt = select(func.count(Notification.id)).where(
            Notification.user_id == user_id, Notification.is_archived == True
        )
        archived = self.db.execute(archived_stmt).scalar_one()

        # Group by priority (not archived)
        priority_stmt = select(Notification.priority, func.count(Notification.id)).where(
            Notification.user_id == user_id, Notification.is_archived == False
        ).group_by(Notification.priority)
        
        priority_stats = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
        for row in self.db.execute(priority_stmt).all():
            if row[0] in priority_stats:
                priority_stats[row[0]] = row[1]

        # Group by type (not archived)
        type_stmt = select(Notification.type, func.count(Notification.id)).where(
            Notification.user_id == user_id, Notification.is_archived == False
        ).group_by(Notification.type)
        
        type_stats = {}
        for row in self.db.execute(type_stmt).all():
            type_stats[row[0]] = row[1]

        return {
            "total": total,
            "unread": unread,
            "read": read,
            "archived": archived,
            "by_priority": priority_stats,
            "by_type": type_stats
        }
