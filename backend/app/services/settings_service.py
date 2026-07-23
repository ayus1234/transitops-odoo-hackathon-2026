"""
Settings service layer containing business logic for admin operations.
"""
from typing import List, Tuple, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.settings import ApplicationSettings, OrganizationSettings
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.schemas.settings import (
    ApplicationSettingsUpdate,
    OrganizationSettingsUpdate,
    AdminUserUpdate,
    AdminResetPassword,
    AdminRoleCreate,
    AdminRoleUpdate,
    PermissionAssign,
    PermissionRemove,
)
from app.repositories.settings_repository import (
    ApplicationSettingsRepository,
    OrganizationSettingsRepository,
    PermissionRepository,
    AdminUserRepository,
    AdminRoleRepository,
)
from app.core.security import get_password_hash
from app.utils.exceptions import (
    NotFoundError,
    DuplicateEntryError,
    BusinessLogicError,
    AuthorizationError,
)
from app.services.activity_service import activity_service
from app.schemas.activity import ActivityCreate
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum


# System roles that cannot be deleted
SYSTEM_ROLES = ["Super Admin", "Administrator", "Fleet Manager", "Driver", "Safety Officer", "Financial Analyst", "Dispatcher", "Maintenance Manager", "Technician", "HR/Operations"]
ADMIN_ROLES = ["Super Admin", "Administrator"]


class SettingsService:
    """Service for application and organization settings."""

    def __init__(self, db: Session):
        self.db = db
        self.app_repo = ApplicationSettingsRepository(db)
        self.org_repo = OrganizationSettingsRepository(db)

    # ── Application Settings ─────────────────────────────────

    def get_app_settings(self) -> ApplicationSettings:
        """Get application settings, creating defaults if not exists."""
        settings = self.app_repo.get()
        if not settings:
            settings = self.app_repo.create_default()
        return settings

    def update_app_settings(self, data: ApplicationSettingsUpdate, current_user: User = None) -> ApplicationSettings:
        """Update application settings."""
        settings = self.get_app_settings()
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise BusinessLogicError("No fields provided for update", code="BIZ_010")
        updated_settings = self.app_repo.update(settings, update_data)
        
        if current_user:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.SETTINGS,
                activity_type=ActivityTypeEnum.UPDATED,
                title="App Settings Updated",
                description="Application configuration was modified.",
                severity=SeverityEnum.INFO,
                status="Success",
                user_id=current_user.id
            ))
            
        return updated_settings

    # ── Organization Settings ────────────────────────────────

    def get_org_settings(self) -> OrganizationSettings:
        """Get organization settings, creating defaults if not exists."""
        org = self.org_repo.get()
        if not org:
            org = self.org_repo.create_default()
        return org

    def update_org_settings(self, data: OrganizationSettingsUpdate, current_user: User = None) -> OrganizationSettings:
        """Update organization settings."""
        org = self.get_org_settings()
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise BusinessLogicError("No fields provided for update", code="BIZ_010")
        updated_org = self.org_repo.update(org, update_data)
        
        if current_user:
            activity_service.log_activity(self.db, ActivityCreate(
                module=ModuleEnum.SETTINGS,
                activity_type=ActivityTypeEnum.UPDATED,
                title="Org Settings Updated",
                description="Organization configuration was modified.",
                severity=SeverityEnum.INFO,
                status="Success",
                user_id=current_user.id
            ))
            
        return updated_org


class AdminUserService:
    """Service for admin user management."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = AdminUserRepository(db)
        self.role_repo = AdminRoleRepository(db)

    def get_users(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        role_id: Optional[UUID] = None,
    ) -> Tuple[List[User], int]:
        """Get paginated list of users."""
        skip = (page - 1) * page_size
        return self.user_repo.get_all(
            skip=skip, limit=page_size,
            search=search, is_active=is_active, role_id=role_id,
        )

    def get_user(self, user_id: UUID) -> User:
        """Get a user by ID."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        return user

    def update_user(self, user_id: UUID, data: AdminUserUpdate, current_user: User) -> User:
        """Update a user's profile (admin)."""
        user = self.get_user(user_id)
        update_data = data.model_dump(exclude_unset=True)

        # Validate role_id if provided
        if "role_id" in update_data:
            role = self.role_repo.get_by_id(update_data["role_id"])
            if not role:
                raise NotFoundError(f"Role with ID {update_data['role_id']} not found")

            # Prevent removing own admin role
            if str(user.id) == str(current_user.id) and current_user.role.name in ADMIN_ROLES:
                new_role = self.role_repo.get_by_id(update_data["role_id"])
                if new_role and new_role.name not in ADMIN_ROLES:
                    raise BusinessLogicError(
                        "Cannot remove your own admin role",
                        code="BIZ_011"
                    )

        return self.user_repo.update(user, update_data)

    def enable_user(self, user_id: UUID) -> User:
        """Enable a user account."""
        user = self.get_user(user_id)
        if user.is_active:
            raise BusinessLogicError("User is already active", code="BIZ_012")
        return self.user_repo.update(user, {"is_active": True})

    def disable_user(self, user_id: UUID, current_user: User) -> User:
        """Disable a user account."""
        user = self.get_user(user_id)

        if not user.is_active:
            raise BusinessLogicError("User is already disabled", code="BIZ_013")

        # Prevent disabling yourself
        if str(user.id) == str(current_user.id):
            raise BusinessLogicError(
                "Cannot disable your own account",
                code="BIZ_014"
            )

        # Prevent disabling the last active administrator
        if user.role.name in ADMIN_ROLES:
            active_admins = self.user_repo.count_active_admins(ADMIN_ROLES)
            if active_admins <= 1:
                raise BusinessLogicError(
                    "Cannot disable the last active administrator. "
                    "Promote another user first.",
                    code="BIZ_015"
                )

        return self.user_repo.update(user, {"is_active": False})

    def reset_password(self, user_id: UUID, data: AdminResetPassword) -> User:
        """Admin reset of a user's password."""
        user = self.get_user(user_id)
        hashed = get_password_hash(data.new_password)
        return self.user_repo.update(user, {"password_hash": hashed})


class AdminRoleService:
    """Service for admin role management."""

    def __init__(self, db: Session):
        self.db = db
        self.role_repo = AdminRoleRepository(db)

    def get_roles(self) -> List[Role]:
        """Get all roles."""
        return self.role_repo.get_all()

    def get_role(self, role_id: UUID) -> Role:
        """Get role by ID."""
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise NotFoundError(f"Role with ID {role_id} not found")
        return role

    def create_role(self, data: AdminRoleCreate) -> Role:
        """Create a new role."""
        if self.role_repo.exists_by_name(data.name):
            raise DuplicateEntryError(f"Role with name '{data.name}' already exists")
        return self.role_repo.create(data.name, data.permissions)

    def update_role(self, role_id: UUID, data: AdminRoleUpdate) -> Role:
        """Update an existing role."""
        role = self.get_role(role_id)
        update_data = data.model_dump(exclude_unset=True)

        # Check name uniqueness if being changed
        if "name" in update_data and update_data["name"] != role.name:
            if self.role_repo.exists_by_name(update_data["name"], exclude_id=role_id):
                raise DuplicateEntryError(
                    f"Role with name '{update_data['name']}' already exists"
                )

        return self.role_repo.update(role, update_data)

    def delete_role(self, role_id: UUID) -> None:
        """Delete a role."""
        role = self.get_role(role_id)

        # Prevent deleting system roles
        if role.name in SYSTEM_ROLES:
            raise BusinessLogicError(
                f"Cannot delete system role '{role.name}'",
                code="BIZ_016"
            )

        # Prevent deleting role with assigned users
        user_count = self.role_repo.count_users(role_id)
        if user_count > 0:
            raise BusinessLogicError(
                f"Cannot delete role '{role.name}' — "
                f"{user_count} user(s) are still assigned to it. "
                "Reassign them first.",
                code="BIZ_017"
            )

        self.role_repo.delete(role)


class PermissionService:
    """Service for permission management."""

    def __init__(self, db: Session):
        self.db = db
        self.perm_repo = PermissionRepository(db)
        self.role_repo = AdminRoleRepository(db)

    def get_permissions(self) -> List[Permission]:
        """Get all registered permissions."""
        return self.perm_repo.get_all()

    def assign_permission(self, data: PermissionAssign, current_user: User) -> Role:
        """
        Assign a permission to a role.
        
        Only Super Admin (Fleet Manager) can manage permissions.
        """
        self._check_super_admin(current_user)

        role = self.role_repo.get_by_id(data.role_id)
        if not role:
            raise NotFoundError(f"Role with ID {data.role_id} not found")

        # Add permission to role's JSON permissions
        permissions = dict(role.permissions or {})
        resource_perms = list(permissions.get(data.resource, []))

        if data.action in resource_perms:
            raise BusinessLogicError(
                f"Permission '{data.resource}:{data.action}' already assigned to role '{role.name}'",
                code="BIZ_018"
            )

        resource_perms.append(data.action)
        permissions[data.resource] = resource_perms

        return self.role_repo.update(role, {"permissions": permissions})

    def remove_permission(self, data: PermissionRemove, current_user: User) -> Role:
        """
        Remove a permission from a role.
        
        Only Super Admin (Fleet Manager) can manage permissions.
        """
        self._check_super_admin(current_user)

        role = self.role_repo.get_by_id(data.role_id)
        if not role:
            raise NotFoundError(f"Role with ID {data.role_id} not found")

        permissions = dict(role.permissions or {})
        resource_perms = list(permissions.get(data.resource, []))

        if data.action not in resource_perms:
            raise BusinessLogicError(
                f"Permission '{data.resource}:{data.action}' is not assigned to role '{role.name}'",
                code="BIZ_019"
            )

        resource_perms.remove(data.action)
        if resource_perms:
            permissions[data.resource] = resource_perms
        else:
            permissions.pop(data.resource, None)

        return self.role_repo.update(role, {"permissions": permissions})

    def _check_super_admin(self, user: User) -> None:
        """Verify user has super admin privileges."""
        if user.role.name not in ADMIN_ROLES:
            raise AuthorizationError(
                "Only Super Admin and Administrator can manage permissions"
            )
