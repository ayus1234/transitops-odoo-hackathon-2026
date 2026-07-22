from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_active_user, RoleChecker
from app.models.user import User
from app.schemas.rbac import (
    PermissionMatrix, RoleCreate, RoleUpdate, RoleResponse, 
    RoleCloneRequest, UserRoleAssignment, PermissionAuditLogResponse,
    TEMPLATES
)
from app.repositories.rbac_repository import RBACRepository
from app.services.rbac_service import RBACService

router = APIRouter()

def get_rbac_service(db: Session = Depends(get_db)) -> RBACService:
    repo = RBACRepository(db)
    return RBACService(repo)

@router.get("/permissions", response_model=List[PermissionMatrix])
def get_permission_matrix(
    service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get the full matrix of configurable permissions in the system."""
    return service.get_permission_matrix()

@router.get("/permissions/templates")
def get_permission_templates(
    current_user: User = Depends(get_current_active_user)
):
    """Get static role templates for UI quick-start."""
    return TEMPLATES

@router.get("/roles", response_model=List[RoleResponse])
def get_roles(
    is_custom: Optional[bool] = Query(None),
    skip: int = 0,
    limit: int = 100,
    service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of roles, optionally filtered by custom status."""
    roles, _ = service.repo.get_roles(is_custom=is_custom, skip=skip, limit=limit)
    return roles

@router.post("/custom-roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_custom_role(
    schema: RoleCreate,
    service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(RoleChecker(["Super Admin", "Administrator", "Fleet Manager"]))
):
    """Create a new custom role."""
    return service.create_custom_role(schema, current_user)

@router.post("/custom-roles/{role_id}/clone", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def clone_role(
    role_id: UUID,
    schema: RoleCloneRequest,
    service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(RoleChecker(["Super Admin", "Administrator", "Fleet Manager"]))
):
    """Clone an existing role into a new custom role."""
    return service.clone_role(role_id, schema, current_user)

@router.put("/custom-roles/{role_id}", response_model=RoleResponse)
def update_custom_role(
    role_id: UUID,
    schema: RoleUpdate,
    service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(RoleChecker(["Super Admin", "Administrator", "Fleet Manager"]))
):
    """Update a custom role's permissions or details."""
    return service.update_role(role_id, schema, current_user)

@router.post("/user-roles", response_model=Dict[str, str])
def assign_user_roles(
    schema: UserRoleAssignment,
    service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(RoleChecker(["Super Admin", "Administrator"]))
):
    """Assign primary and additional roles to a user."""
    service.assign_user_roles(schema, current_user)
    return {"status": "success", "message": "Roles assigned successfully"}

@router.get("/permissions/audit", response_model=List[PermissionAuditLogResponse])
def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(RoleChecker(["Super Admin", "Administrator", "Fleet Manager"]))
):
    """Get audit logs for RBAC changes."""
    logs, _ = service.repo.get_audit_logs(skip=skip, limit=limit)
    return logs

@router.get("/permissions/export", response_class=PlainTextResponse)
def export_audit_logs_csv(
    service: RBACService = Depends(get_rbac_service),
    current_user: User = Depends(RoleChecker(["Super Admin", "Administrator", "Fleet Manager"]))
):
    """Export RBAC audit logs to CSV."""
    csv_data = service.export_audit_csv()
    return PlainTextResponse(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=rbac_audit_{__import__('datetime').datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"}
    )
