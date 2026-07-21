"""
Settings repository for database operations on settings tables.
"""
from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.settings import ApplicationSettings, OrganizationSettings
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User


class ApplicationSettingsRepository:
    """Repository for application settings database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get(self) -> Optional[ApplicationSettings]:
        """Get the singleton application settings row."""
        return self.db.query(ApplicationSettings).filter(
            ApplicationSettings.key == "default"
        ).first()

    def create_default(self) -> ApplicationSettings:
        """Create default application settings if not exists."""
        settings = ApplicationSettings(key="default")
        self.db.add(settings)
        self.db.commit()
        self.db.refresh(settings)
        return settings

    def update(self, settings: ApplicationSettings, data: dict) -> ApplicationSettings:
        """Update application settings."""
        for field, value in data.items():
            setattr(settings, field, value)
        self.db.commit()
        self.db.refresh(settings)
        return settings


class OrganizationSettingsRepository:
    """Repository for organization settings database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get(self) -> Optional[OrganizationSettings]:
        """Get the singleton organization settings row."""
        return self.db.query(OrganizationSettings).filter(
            OrganizationSettings.key == "default"
        ).first()

    def create_default(self) -> OrganizationSettings:
        """Create default organization settings if not exists."""
        org = OrganizationSettings(key="default")
        self.db.add(org)
        self.db.commit()
        self.db.refresh(org)
        return org

    def update(self, org: OrganizationSettings, data: dict) -> OrganizationSettings:
        """Update organization settings."""
        for field, value in data.items():
            setattr(org, field, value)
        self.db.commit()
        self.db.refresh(org)
        return org


class PermissionRepository:
    """Repository for permission database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Permission]:
        """Get all permissions."""
        return self.db.query(Permission).order_by(
            Permission.resource, Permission.action
        ).all()

    def get_by_id(self, permission_id: UUID) -> Optional[Permission]:
        """Get permission by ID."""
        return self.db.query(Permission).filter(Permission.id == permission_id).first()

    def get_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by unique name."""
        return self.db.query(Permission).filter(Permission.name == name).first()

    def create(self, name: str, resource: str, action: str, description: str = None, is_system: bool = False) -> Permission:
        """Create a new permission."""
        perm = Permission(
            name=name,
            resource=resource,
            action=action,
            description=description,
            is_system=is_system,
        )
        self.db.add(perm)
        self.db.commit()
        self.db.refresh(perm)
        return perm


class AdminUserRepository:
    """Repository for admin user management operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        role_id: Optional[UUID] = None,
    ) -> Tuple[List[User], int]:
        """Get all users with optional filters."""
        query = self.db.query(User)

        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if role_id:
            query = query.filter(User.role_id == role_id)

        total = query.count()
        users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        return users, total

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def update(self, user: User, data: dict) -> User:
        """Update user fields."""
        for field, value in data.items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def count_active_admins(self, admin_role_names: List[str]) -> int:
        """Count active users with admin roles."""
        return self.db.query(User).join(Role).filter(
            User.is_active == True,
            Role.name.in_(admin_role_names),
        ).count()


class AdminRoleRepository:
    """Repository for admin role management operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Role]:
        """Get all roles."""
        return self.db.query(Role).order_by(Role.created_at.asc()).all()

    def get_by_id(self, role_id: UUID) -> Optional[Role]:
        """Get role by ID."""
        return self.db.query(Role).filter(Role.id == role_id).first()

    def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        return self.db.query(Role).filter(Role.name == name).first()

    def exists_by_name(self, name: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if role with name exists."""
        query = self.db.query(Role).filter(Role.name == name)
        if exclude_id:
            query = query.filter(Role.id != exclude_id)
        return query.first() is not None

    def create(self, name: str, permissions: dict) -> Role:
        """Create a new role."""
        role = Role(name=name, permissions=permissions)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update(self, role: Role, data: dict) -> Role:
        """Update a role."""
        for field, value in data.items():
            setattr(role, field, value)
        self.db.commit()
        self.db.refresh(role)
        return role

    def delete(self, role: Role) -> None:
        """Delete a role."""
        self.db.delete(role)
        self.db.commit()

    def count_users(self, role_id: UUID) -> int:
        """Count users assigned to a role."""
        return self.db.query(User).filter(User.role_id == role_id).count()
