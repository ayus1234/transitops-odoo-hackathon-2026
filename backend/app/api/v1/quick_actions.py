"""
API router for Quick Actions module.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.quick_action import (
    QuickActionListResponse, 
    QuickActionResponse,
    QuickActionStatistics, 
    FavoriteActionRequest,
    FavoriteActionAddRequest,
    FavoriteActionRemoveRequest,
    PermissionsResponse,
    RecentActionResponse,
    ExecuteActionResponse
)
from fastapi.responses import Response
from app.services.quick_action_service import QuickActionService

router = APIRouter()


@router.get("", response_model=QuickActionListResponse)
def list_available_actions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return all active actions available for the authenticated user, filtered by RBAC permissions."""
    service = QuickActionService(db)
    actions = service.get_available_actions(current_user)
    return {"success": True, "data": actions}


@router.get("/favorites", response_model=QuickActionListResponse)
def list_favorite_actions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return favorite actions for the authenticated user."""
    service = QuickActionService(db)
    actions = service.get_favorite_actions(current_user)
    return {"success": True, "data": actions}


@router.get("/recent", response_model=dict)
def list_recent_actions(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return recently executed actions tracked per user."""
    service = QuickActionService(db)
    actions = service.get_recent_actions(current_user, limit)
    return {"success": True, "data": actions}


@router.get("/statistics", response_model=dict)
def get_action_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overall quick action usage statistics for the user."""
    service = QuickActionService(db)
    stats = service.get_statistics(current_user)
    return {"success": True, "data": stats}


@router.get("/search", response_model=QuickActionListResponse)
def search_actions(
    keyword: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search available actions by keyword or category."""
    service = QuickActionService(db)
    actions = service.search_actions(current_user, keyword, category)
    return {"success": True, "data": actions}


@router.patch("/{action_id}/favorite", response_model=dict)
def toggle_favorite(
    action_id: UUID,
    request: FavoriteActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle the favorite status of a specific action for the authenticated user."""
    service = QuickActionService(db)
    action = service.toggle_favorite(action_id, request.is_favorite, current_user)
    return {"success": True, "data": action}


@router.post("/{action_id}/execute", response_model=dict, status_code=status.HTTP_201_CREATED)
def execute_action(
    action_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Log the execution of the action and return the target route + metadata.
    Does NOT perform the actual CRUD operation.
    """
    service = QuickActionService(db)
    result = service.execute_action(action_id, current_user)
    return {"success": True, "data": result}

@router.get("/permissions", response_model=dict)
def get_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get grouped allowed and restricted actions based on user permissions."""
    service = QuickActionService(db)
    result = service.get_permissions(current_user)
    return {"success": True, "data": result}

@router.post("/favorites/add", response_model=dict)
def add_favorite(
    request: FavoriteActionAddRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a quick action to favorites."""
    service = QuickActionService(db)
    action = service.add_favorite(request.action_id, current_user)
    return {"success": True, "data": action}

@router.post("/favorites/remove", response_model=dict)
def remove_favorite(
    request: FavoriteActionRemoveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a quick action from favorites."""
    service = QuickActionService(db)
    action = service.remove_favorite(request.action_id, current_user)
    return {"success": True, "data": action}

@router.get("/export/{export_type}")
def export_data(
    export_type: str,
    format: str = Query("csv", description="Format to export: csv, json, or pdf"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export recent, favorites, or statistics."""
    service = QuickActionService(db)
    filename, content, media_type = service.export_data(current_user, format.lower(), export_type.lower())
    
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename.split('.')[0]}_{__import__('datetime').datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.{filename.split('.')[1]}"}
    )
