from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from uuid import UUID

from app.models.role import Role
from app.models.user import User
from app.models.permission_audit import PermissionAuditLog

class RBACRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_role(self, role_id: UUID) -> Optional[Role]:
        return self.db.query(Role).filter(Role.id == role_id).first()
        
    def get_role_by_name(self, name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == name).first()

    def get_roles(self, is_custom: Optional[bool] = None, skip: int = 0, limit: int = 100) -> Tuple[List[Role], int]:
        query = self.db.query(Role)
        if is_custom is not None:
            query = query.filter(Role.is_custom == is_custom)
        total = query.count()
        roles = query.order_by(Role.name).offset(skip).limit(limit).all()
        return roles, total

    def create_role(self, role: Role) -> Role:
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update_role(self, role: Role) -> Role:
        self.db.commit()
        self.db.refresh(role)
        return role
        
    def delete_role(self, role: Role) -> None:
        self.db.delete(role)
        self.db.commit()

    def get_user(self, user_id: UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
        
    def assign_user_roles(self, user: User, primary_role: Role, additional_roles: List[Role]) -> User:
        user.role = primary_role
        user.additional_roles = additional_roles
        self.db.commit()
        self.db.refresh(user)
        return user

    def log_audit(self, audit: PermissionAuditLog) -> PermissionAuditLog:
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(audit)
        return audit

    def get_audit_logs(self, skip: int = 0, limit: int = 100) -> Tuple[List[PermissionAuditLog], int]:
        query = self.db.query(PermissionAuditLog).order_by(desc(PermissionAuditLog.timestamp))
        total = query.count()
        logs = query.offset(skip).limit(limit).all()
        return logs, total
