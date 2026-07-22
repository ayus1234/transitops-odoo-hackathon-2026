from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import HTTPException, status
import json
import csv
from io import StringIO

from app.schemas.rbac import RoleCreate, RoleUpdate, RoleCloneRequest, UserRoleAssignment, TEMPLATES, PermissionMatrix
from app.repositories.rbac_repository import RBACRepository
from app.models.role import Role
from app.models.user import User
from app.models.permission_audit import PermissionAuditLog

class RBACService:
    def __init__(self, repo: RBACRepository):
        self.repo = repo
        
    def _create_audit(self, actor_id: Optional[UUID], action: str, module: Optional[str] = None, 
                      target_role_id: Optional[UUID] = None, target_user_id: Optional[UUID] = None, 
                      prev_val: Optional[dict] = None, new_val: Optional[dict] = None):
        audit = PermissionAuditLog(
            user_id=actor_id,
            action=action,
            module=module,
            target_role_id=target_role_id,
            target_user_id=target_user_id,
            previous_value=prev_val,
            new_value=new_val
        )
        self.repo.log_audit(audit)

    def get_permission_matrix(self) -> List[PermissionMatrix]:
        # Return all possible modules and actions in the system
        matrix = [
            {"module": "dashboard", "permissions": ["read"]},
            {"module": "reports", "permissions": ["read", "export"]},
            {"module": "vehicles", "permissions": ["read", "create", "update", "delete"]},
            {"module": "drivers", "permissions": ["read", "create", "update", "delete"]},
            {"module": "trips", "permissions": ["read", "create", "update", "delete"]},
            {"module": "maintenance", "permissions": ["read", "create", "update", "delete", "approve"]},
            {"module": "inventory", "permissions": ["read", "create", "update", "delete", "approve"]},
            {"module": "expenses", "permissions": ["read", "create", "update", "delete", "approve", "export"]},
            {"module": "fuel", "permissions": ["read", "create", "update", "delete"]},
            {"module": "settings", "permissions": ["read", "update"]},
        ]
        return [PermissionMatrix(**m) for m in matrix]

    def create_custom_role(self, schema: RoleCreate, actor: User) -> Role:
        if self.repo.get_role_by_name(schema.name):
            raise HTTPException(status_code=400, detail="Role name already exists")
            
        role = Role(
            name=schema.name,
            description=schema.description,
            permissions=schema.permissions,
            is_custom=True,
            parent_role_id=schema.parent_role_id
        )
        role = self.repo.create_role(role)
        
        self._create_audit(
            actor_id=actor.id,
            action="CREATE_ROLE",
            target_role_id=role.id,
            new_val={"name": role.name, "permissions": role.permissions}
        )
        return role

    def update_role(self, role_id: UUID, schema: RoleUpdate, actor: User) -> Role:
        role = self.repo.get_role(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
            
        prev_perms = role.permissions.copy()
        
        if schema.name:
            role.name = schema.name
        if schema.description:
            role.description = schema.description
        if schema.permissions is not None:
            role.permissions = schema.permissions
        if schema.parent_role_id:
            role.parent_role_id = schema.parent_role_id
            
        role = self.repo.update_role(role)
        
        self._create_audit(
            actor_id=actor.id,
            action="UPDATE_ROLE",
            target_role_id=role.id,
            prev_val={"permissions": prev_perms},
            new_val={"permissions": role.permissions}
        )
        return role

    def clone_role(self, role_id: UUID, schema: RoleCloneRequest, actor: User) -> Role:
        base_role = self.repo.get_role(role_id)
        if not base_role:
            raise HTTPException(status_code=404, detail="Base role not found")
            
        if self.repo.get_role_by_name(schema.new_name):
            raise HTTPException(status_code=400, detail="Role name already exists")
            
        new_role = Role(
            name=schema.new_name,
            description=schema.description or f"Cloned from {base_role.name}",
            permissions=base_role.permissions.copy(),
            is_custom=True,
            parent_role_id=base_role.id
        )
        new_role = self.repo.create_role(new_role)
        
        self._create_audit(
            actor_id=actor.id,
            action="CLONE_ROLE",
            target_role_id=new_role.id,
            prev_val={"base_role_id": str(base_role.id)},
            new_val={"name": new_role.name}
        )
        return new_role

    def assign_user_roles(self, schema: UserRoleAssignment, actor: User) -> User:
        target_user = self.repo.get_user(schema.user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
            
        primary_role = self.repo.get_role(schema.primary_role_id)
        if not primary_role:
            raise HTTPException(status_code=404, detail="Primary role not found")
            
        additional_roles = []
        for rid in schema.additional_role_ids:
            r = self.repo.get_role(rid)
            if not r:
                raise HTTPException(status_code=404, detail=f"Additional role {rid} not found")
            additional_roles.append(r)
            
        prev_roles = {
            "primary": str(target_user.role_id) if target_user.role_id else None,
            "additional": [str(r.id) for r in target_user.additional_roles] if target_user.additional_roles else []
        }
        
        target_user = self.repo.assign_user_roles(target_user, primary_role, additional_roles)
        
        new_roles = {
            "primary": str(primary_role.id),
            "additional": [str(r.id) for r in additional_roles]
        }
        
        self._create_audit(
            actor_id=actor.id,
            action="ASSIGN_ROLES",
            target_user_id=target_user.id,
            prev_val=prev_roles,
            new_val=new_roles
        )
        return target_user

    def export_audit_csv(self) -> str:
        logs, _ = self.repo.get_audit_logs(skip=0, limit=1000)
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Timestamp", "Actor ID", "Action", "Target User ID", "Target Role ID", "Changes"])
        
        for log in logs:
            writer.writerow([
                str(log.id),
                log.timestamp.isoformat(),
                str(log.user_id) if log.user_id else "System",
                log.action,
                str(log.target_user_id) if log.target_user_id else "",
                str(log.target_role_id) if log.target_role_id else "",
                json.dumps(log.new_value) if log.new_value else ""
            ])
            
        return output.getvalue()
