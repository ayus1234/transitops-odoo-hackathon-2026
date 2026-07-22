from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from math import ceil

from app.api.deps import get_db, get_current_user, RoleChecker
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate, 
    NotificationResponse, 
    NotificationListResponse, 
    NotificationStatistics
)
from app.services.notification_service import NotificationService

router = APIRouter()
admin_required = RoleChecker(["Super Admin", "Fleet Manager", "System Administrator"])


@router.get("/", response_model=NotificationListResponse)
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    priority: Optional[str] = None,
    type: Optional[str] = None,
    category: Optional[str] = None,
    module_name: Optional[str] = None,
    is_read: Optional[bool] = None,
    is_archived: Optional[bool] = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve user notifications with pagination and filtering.
    """
    service = NotificationService(db)
    total, notifications = service.get_user_notifications(
        user_id=current_user.id,
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
    
    return NotificationListResponse(
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        size=len(notifications),
        pages=ceil(total / limit) if limit > 0 else 1,
        data=notifications
    )


@router.get("/unread", response_model=NotificationListResponse)
def get_unread_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve unread user notifications.
    """
    service = NotificationService(db)
    total, notifications = service.get_user_notifications(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        is_read=False,
        is_archived=False
    )
    
    return NotificationListResponse(
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        size=len(notifications),
        pages=ceil(total / limit) if limit > 0 else 1,
        data=notifications
    )

@router.get("/archived", response_model=NotificationListResponse)
def get_archived_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve archived user notifications.
    """
    service = NotificationService(db)
    total, notifications = service.get_user_notifications(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        is_archived=True
    )
    
    return NotificationListResponse(
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        size=len(notifications),
        pages=ceil(total / limit) if limit > 0 else 1,
        data=notifications
    )

@router.get("/search", response_model=NotificationListResponse)
def search_notifications(
    q: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Search notifications by title, description, category, module.
    """
    service = NotificationService(db)
    total, notifications = service.get_user_notifications(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        search=q
    )
    
    return NotificationListResponse(
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        size=len(notifications),
        pages=ceil(total / limit) if limit > 0 else 1,
        data=notifications
    )

@router.get("/filter", response_model=NotificationListResponse)
def filter_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    priority: Optional[str] = None,
    category: Optional[str] = None,
    type: Optional[str] = None,
    module: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Filter notifications. Status maps to is_read/is_archived.
    """
    is_read = None
    is_archived = False
    
    if status == "read":
        is_read = True
    elif status == "unread":
        is_read = False
    elif status == "archived":
        is_archived = True
        
    service = NotificationService(db)
    total, notifications = service.get_user_notifications(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        priority=priority,
        category=category,
        type=type,
        module_name=module,
        is_read=is_read,
        is_archived=is_archived
    )
    
    return NotificationListResponse(
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        size=len(notifications),
        pages=ceil(total / limit) if limit > 0 else 1,
        data=notifications
    )


@router.get("/statistics", response_model=NotificationStatistics)
def get_notification_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get statistics for current user's notifications.
    """
    service = NotificationService(db)
    return service.get_statistics(current_user.id)


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a specific notification by ID.
    """
    service = NotificationService(db)
    return service.get_notification(notification_id, current_user.id)


@router.post("/", response_model=NotificationResponse, dependencies=[Depends(admin_required)], status_code=status.HTTP_201_CREATED)
def create_notification(
    notification_in: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a notification for a specific user (Admin only).
    """
    service = NotificationService(db)
    return service.create_notification(current_user.id, notification_in)


@router.post("/{notification_id}/mark-read", response_model=NotificationResponse)
@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Mark a notification as read.
    """
    service = NotificationService(db)
    return service.mark_read(notification_id, current_user.id)


@router.patch("/{notification_id}/unread", response_model=NotificationResponse)
def mark_notification_unread(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Mark a notification as unread.
    """
    service = NotificationService(db)
    return service.mark_unread(notification_id, current_user.id)


@router.post("/mark-all-read")
@router.patch("/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Mark all unread notifications as read.
    """
    service = NotificationService(db)
    count = service.mark_all_read(current_user.id)
    return {"message": f"Successfully marked {count} notifications as read", "count": count}


@router.post("/{notification_id}/archive", response_model=NotificationResponse)
@router.patch("/{notification_id}/archive", response_model=NotificationResponse)
def archive_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Archive a notification.
    """
    service = NotificationService(db)
    return service.archive(notification_id, current_user.id)

@router.post("/{notification_id}/unarchive", response_model=NotificationResponse)
def unarchive_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Unarchive a notification.
    """
    service = NotificationService(db)
    return service.unarchive(notification_id, current_user.id)

@router.post("/{notification_id}/execute")
def execute_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Execute a notification, marking it as read, logging activity, and returning the target route.
    """
    service = NotificationService(db)
    return service.execute_notification(notification_id, current_user.id)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete a notification.
    """
    service = NotificationService(db)
    service.delete(notification_id, current_user.id)
    return None
