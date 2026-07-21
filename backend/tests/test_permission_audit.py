import pytest
from uuid import uuid4
from datetime import datetime
from app.models.permission_audit import PermissionAuditLog

def test_permission_audit_log_creation():
    log_id = uuid4()
    actor_id = uuid4()
    target_id = uuid4()
    
    log = PermissionAuditLog(
        id=log_id,
        user_id=actor_id,
        action="CREATE_ROLE",
        module="roles",
        target_role_id=target_id,
        previous_value={},
        new_value={"name": "New Role"}
    )
    
    assert log.id == log_id
    assert log.action == "CREATE_ROLE"
    assert log.module == "roles"
    assert log.new_value == {"name": "New Role"}
