import pytest
from uuid import uuid4
from app.models.role import Role

def test_custom_role_creation():
    role = Role(name="Custom Fleet Manager", is_custom=True, permissions={"dashboard": ["read"]})
    assert role.name == "Custom Fleet Manager"
    assert role.is_custom is True
    assert "dashboard" in role.permissions

def test_role_cloning_logic():
    base_role = Role(name="Base", permissions={"vehicles": ["read"]}, id=uuid4())
    cloned_role = Role(
        name="Cloned", 
        permissions=base_role.permissions.copy(), 
        is_custom=True, 
        parent_role_id=base_role.id
    )
    
    assert cloned_role.name == "Cloned"
    assert cloned_role.permissions == base_role.permissions
    assert cloned_role.parent_role_id == base_role.id
    assert cloned_role.is_custom is True
