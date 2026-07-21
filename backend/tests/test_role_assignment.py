import pytest
from uuid import uuid4
from app.models.user import User
from app.models.role import Role

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
    
    # Primary role
    assert user.has_permission("dashboard", "read") is True
    
    # Additional roles
    assert user.has_permission("vehicles", "read") is True
    assert user.has_permission("trips", "create") is True
    
    # Missing perms
    assert user.has_permission("vehicles", "create") is False
