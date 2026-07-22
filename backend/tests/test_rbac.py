import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from app.models.user import User
from app.models.role import Role

def test_user_has_permission_primary_role():
    role = Role(name="Test Role", permissions={"vehicles": ["read", "create"]})
    user = User(
        id=uuid4(),
        email="test@example.com",
        first_name="Test",
        last_name="User",
        role=role
    )
    
    assert user.has_permission("vehicles", "read") is True
    assert user.has_permission("vehicles", "create") is True
    assert user.has_permission("vehicles", "delete") is False
    assert user.has_permission("drivers", "read") is False

def test_user_has_permission_additional_roles():
    primary_role = Role(name="Base", permissions={"dashboard": ["read"]})
    additional_role_1 = Role(name="Add1", permissions={"vehicles": ["read"]})
    additional_role_2 = Role(name="Add2", permissions={"trips": ["create", "read"]})
    
    user = User(
        id=uuid4(),
        email="multi@example.com",
        first_name="Multi",
        last_name="Role",
        role=primary_role,
        additional_roles=[additional_role_1, additional_role_2]
    )
    
    # Implicit perms
    assert user.has_permission("dashboard", "read") is True
    
    # Primary role
    assert user.has_permission("dashboard", "read") is True
    
    # Additional roles
    assert user.has_permission("vehicles", "read") is True
    assert user.has_permission("trips", "create") is True
    
    # Missing perms
    assert user.has_permission("vehicles", "create") is False

def test_permission_inheritance():
    parent_role = Role(name="Parent", permissions={"vehicles": ["read", "update"]})
    child_role = Role(name="Child", permissions={"drivers": ["read"]}, parent=parent_role)
    
    user = User(
        id=uuid4(),
        email="child@example.com",
        first_name="Child",
        last_name="Role",
        role=child_role
    )
    
    assert user.has_permission("drivers", "read") is True
    assert user.has_permission("vehicles", "read") is True
    assert user.has_permission("vehicles", "update") is True
    assert user.has_permission("vehicles", "delete") is False
