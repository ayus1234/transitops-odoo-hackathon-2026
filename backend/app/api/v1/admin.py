"""
Admin Settings & Permissions API endpoints.

Provides enterprise administration for:
- Application Settings (GET, PUT)
- Organization Settings (GET, PUT)
- User Management (GET, GET by ID, UPDATE, ENABLE, DISABLE, RESET PASSWORD)
- Role Management (GET, CREATE, UPDATE, DELETE)
- Permission Management (GET, ASSIGN, REMOVE)
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, RoleChecker
from app.models.user import User
from app.schemas.settings import (
    ApplicationSettingsResponse,
    ApplicationSettingsUpdate,
    OrganizationSettingsResponse,
    OrganizationSettingsUpdate,
    PermissionResponse,
    PermissionAssign,
    PermissionRemove,
    AdminUserUpdate,
    AdminUserResponse,
    AdminResetPassword,
    AdminRoleCreate,
    AdminRoleUpdate,
)
from app.schemas.role import RoleResponse
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.services.settings_service import (
    SettingsService,
    AdminUserService,
    AdminRoleService,
    PermissionService,
)


router = APIRouter()

# Only Super Admin, Administrator, and Fleet Manager can access settings endpoints
admin_only = RoleChecker(["Super Admin", "Administrator", "Fleet Manager"])


# ═══════════════════════════════════════════════════════════════
# APPLICATION SETTINGS
# ═══════════════════════════════════════════════════════════════

@router.get("/settings", response_model=ApplicationSettingsResponse, tags=["Admin Settings"])
def get_application_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Get application-level settings.
    
    Permissions: Fleet Manager only
    """
    service = SettingsService(db)
    return ApplicationSettingsResponse.model_validate(service.get_app_settings())


@router.put("/settings", response_model=ApplicationSettingsResponse, tags=["Admin Settings"])
def update_application_settings(
    data: ApplicationSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Update application-level settings.
    
    Permissions: Fleet Manager only
    
    Business Rules:
    - Timezone must be a valid timezone
    - Currency must be a valid ISO 4217 code
    - Language must be supported
    """
    service = SettingsService(db)
    return ApplicationSettingsResponse.model_validate(service.update_app_settings(data, current_user))


# ═══════════════════════════════════════════════════════════════
# ORGANIZATION SETTINGS
# ═══════════════════════════════════════════════════════════════

@router.get("/organization", response_model=OrganizationSettingsResponse, tags=["Admin Organization"])
def get_organization_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Get organization-level settings.
    
    Permissions: Fleet Manager only
    """
    service = SettingsService(db)
    return OrganizationSettingsResponse.model_validate(service.get_org_settings())


@router.put("/organization", response_model=OrganizationSettingsResponse, tags=["Admin Organization"])
def update_organization_settings(
    data: OrganizationSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Update organization-level settings.
    
    Permissions: Fleet Manager only
    
    Business Rules:
    - Organization email must be valid
    """
    service = SettingsService(db)
    return OrganizationSettingsResponse.model_validate(service.update_org_settings(data, current_user))


# ═══════════════════════════════════════════════════════════════
# USER MANAGEMENT
# ═══════════════════════════════════════════════════════════════

def _user_to_response(user: User) -> AdminUserResponse:
    """Convert User ORM to AdminUserResponse."""
    return AdminUserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        phone_number=user.phone_number,
        is_active=user.is_active,
        role_id=user.role_id,
        role_name=user.role.name if user.role else "Unknown",
        additional_roles=[{"id": str(r.id), "name": r.name, "is_custom": r.is_custom} for r in user.additional_roles] if getattr(user, 'additional_roles', None) else [],
        last_login=user.last_login,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("/users", response_model=PaginatedResponse[AdminUserResponse], tags=["Admin Users"])
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    role_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    List all users with pagination, search, and filters.
    
    Permissions: Fleet Manager only
    """
    service = AdminUserService(db)
    users, total = service.get_users(
        page=page, page_size=page_size,
        search=search, is_active=is_active, role_id=role_id,
    )
    return PaginatedResponse(
        success=True,
        data=[_user_to_response(u) for u in users],
        pagination=PaginationMeta(
            page=page,
            page_size=page_size,
            total_items=total,
            total_pages=(total + page_size - 1) // page_size,
        ),
    )


@router.get("/users/{user_id}", response_model=AdminUserResponse, tags=["Admin Users"])
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Get a specific user by ID.
    
    Permissions: Fleet Manager only
    """
    service = AdminUserService(db)
    return _user_to_response(service.get_user(user_id))


@router.put("/users/{user_id}", response_model=AdminUserResponse, tags=["Admin Users"])
def update_user(
    user_id: UUID,
    data: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Update a user's profile (admin).
    
    Permissions: Fleet Manager only
    
    Business Rules:
    - Cannot remove own admin role
    """
    service = AdminUserService(db)
    user = service.update_user(user_id, data, current_user)
    return _user_to_response(user)


@router.patch("/users/{user_id}/enable", response_model=SuccessResponse, tags=["Admin Users"])
def enable_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Enable a disabled user account.
    
    Permissions: Fleet Manager only
    """
    service = AdminUserService(db)
    user = service.enable_user(user_id)
    return SuccessResponse(
        success=True,
        message=f"User '{user.full_name}' has been enabled",
        data={"user_id": str(user.id)},
    )


@router.patch("/users/{user_id}/disable", response_model=SuccessResponse, tags=["Admin Users"])
def disable_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Disable an active user account.
    
    Permissions: Fleet Manager only
    
    Business Rules:
    - Cannot disable yourself
    - Cannot disable the last active administrator
    """
    service = AdminUserService(db)
    user = service.disable_user(user_id, current_user)
    return SuccessResponse(
        success=True,
        message=f"User '{user.full_name}' has been disabled",
        data={"user_id": str(user.id)},
    )


@router.post("/users/{user_id}/reset-password", response_model=SuccessResponse, tags=["Admin Users"])
def reset_user_password(
    user_id: UUID,
    data: AdminResetPassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Reset a user's password (admin only).
    
    Permissions: Fleet Manager only
    """
    service = AdminUserService(db)
    user = service.reset_password(user_id, data)
    return SuccessResponse(
        success=True,
        message=f"Password reset for user '{user.full_name}'",
        data={"user_id": str(user.id)},
    )


# ═══════════════════════════════════════════════════════════════
# ROLE MANAGEMENT
# ═══════════════════════════════════════════════════════════════

@router.get("/roles", response_model=List[RoleResponse], tags=["Admin Roles"])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Get all roles.
    
    Permissions: Fleet Manager only
    """
    service = AdminRoleService(db)
    return [RoleResponse.model_validate(r) for r in service.get_roles()]


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED, tags=["Admin Roles"])
def create_role(
    data: AdminRoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Create a new role.
    
    Permissions: Fleet Manager only
    
    Business Rules:
    - Role name must be unique
    """
    service = AdminRoleService(db)
    role = service.create_role(data)
    return RoleResponse.model_validate(role)


@router.put("/roles/{role_id}", response_model=RoleResponse, tags=["Admin Roles"])
def update_role(
    role_id: UUID,
    data: AdminRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Update an existing role.
    
    Permissions: Fleet Manager only
    
    Business Rules:
    - Role name must be unique
    """
    service = AdminRoleService(db)
    role = service.update_role(role_id, data)
    return RoleResponse.model_validate(role)


@router.delete("/roles/{role_id}", response_model=SuccessResponse, tags=["Admin Roles"])
def delete_role(
    role_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Delete a role.
    
    Permissions: Fleet Manager only
    
    Business Rules:
    - Cannot delete system roles
    - Cannot delete roles with assigned users
    """
    service = AdminRoleService(db)
    service.delete_role(role_id)
    return SuccessResponse(success=True, message="Role deleted successfully")


# ═══════════════════════════════════════════════════════════════
# PERMISSION MANAGEMENT
# ═══════════════════════════════════════════════════════════════

@router.get("/permissions", response_model=List[PermissionResponse], tags=["Admin Permissions"])
def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Get all registered permissions.
    
    Permissions: Fleet Manager only
    """
    service = PermissionService(db)
    return [PermissionResponse.model_validate(p) for p in service.get_permissions()]


@router.post("/permissions/assign", response_model=RoleResponse, tags=["Admin Permissions"])
def assign_permission(
    data: PermissionAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Assign a permission to a role.
    
    Permissions: Fleet Manager (Super Admin) only
    
    Business Rules:
    - Only Super Admin can manage permissions
    - Permission names must be unique per role
    """
    service = PermissionService(db)
    role = service.assign_permission(data, current_user)
    return RoleResponse.model_validate(role)


@router.delete("/permissions/remove", response_model=RoleResponse, tags=["Admin Permissions"])
def remove_permission(
    data: PermissionRemove,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """
    Remove a permission from a role.
    
    Permissions: Fleet Manager (Super Admin) only
    
    Business Rules:
    - Only Super Admin can manage permissions
    """
    service = PermissionService(db)
    role = service.remove_permission(data, current_user)
    return RoleResponse.model_validate(role)
