import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from app.models.user import User
from app.models.role import Role
from app.main import app

client = TestClient(app)

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

def test_permission_matrix_endpoint():
    # Requires auth, but for unit testing we can mock or use a test client with a valid token
    pass
