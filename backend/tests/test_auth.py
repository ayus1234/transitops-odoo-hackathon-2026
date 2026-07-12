"""
Test authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User
from app.core.security import get_password_hash


def test_login_success(client: TestClient, db_session: Session):
    """Test successful login."""
    # Create role
    role = Role(name="Fleet Manager", permissions={})
    db_session.add(role)
    db_session.commit()
    
    # Create user
    user = User(
        email="testuser@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="Test",
        last_name="User",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Attempt login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@transitops.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == "testuser@transitops.com"


def test_login_invalid_email(client: TestClient):
    """Test login with invalid email."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@transitops.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_invalid_password(client: TestClient, db_session: Session):
    """Test login with invalid password."""
    # Create role
    role = Role(name="Fleet Manager", permissions={})
    db_session.add(role)
    db_session.commit()
    
    # Create user
    user = User(
        email="testuser@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="Test",
        last_name="User",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Attempt login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "testuser@transitops.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_inactive_user(client: TestClient, db_session: Session):
    """Test login with inactive user."""
    # Create role
    role = Role(name="Fleet Manager", permissions={})
    db_session.add(role)
    db_session.commit()
    
    # Create inactive user
    user = User(
        email="inactive@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="Inactive",
        last_name="User",
        role_id=role.id,
        is_active=False
    )
    db_session.add(user)
    db_session.commit()
    
    # Attempt login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "inactive@transitops.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 403
    assert "inactive" in response.json()["detail"].lower()


def test_get_current_user(client: TestClient, auth_headers: dict):
    """Test getting current user information."""
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "role" in data


def test_get_current_user_no_token(client: TestClient):
    """Test getting current user without token."""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 403


def test_logout(client: TestClient, auth_headers: dict):
    """Test logout endpoint."""
    response = client.post(
        "/api/v1/auth/logout",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["success"] is True
