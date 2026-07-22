"""
Tests for Help Center module.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime

from app.models.help_center import HelpCategory, HelpArticle, SupportTicket, Feedback
from app.models.role import Role
from app.models.user import User
from app.core.security import get_password_hash


@pytest.fixture
def admin_headers(client: TestClient, db_session: Session) -> dict:
    """Create authentication headers for an admin user."""
    # Ensure role exists
    role = db_session.query(Role).filter(Role.name == "System Admin").first()
    if not role:
        role = Role(
            name="System Admin",
            permissions={"all": ["read", "create", "update", "delete"]}
        )
        db_session.add(role)
        db_session.commit()
    
    # Ensure user exists
    user = db_session.query(User).filter(User.email == "admin@transitops.com").first()
    if not user:
        user = User(
            email="admin@transitops.com",
            password_hash=get_password_hash("adminpass123"),
            first_name="Admin",
            last_name="User",
            role_id=role.id,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
    
    # Login to get token
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@transitops.com", "password": "adminpass123"}
    )
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_headers(client: TestClient, db_session: Session) -> dict:
    """Create authentication headers for a regular user."""
    role = db_session.query(Role).filter(Role.name == "Standard User").first()
    if not role:
        role = Role(
            name="Standard User",
            permissions={}
        )
        db_session.add(role)
        db_session.commit()
    
    user = db_session.query(User).filter(User.email == "user@transitops.com").first()
    if not user:
        user = User(
            email="user@transitops.com",
            password_hash=get_password_hash("userpass123"),
            first_name="Test",
            last_name="User",
            role_id=role.id,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
    
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@transitops.com", "password": "userpass123"}
    )
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# Make sure the models are imported BEFORE tables are created
# Base.metadata.create_all is called in conftest, but we must ensure help_center is imported!
import app.models.help_center


def test_create_category_admin(client: TestClient, admin_headers: dict):
    response = client.post(
        "/api/v1/help/categories",
        headers=admin_headers,
        json={
            "name": "General Settings",
            "description": "General settings configuration",
            "display_order": 1
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "General Settings"


def test_create_category_forbidden(client: TestClient, test_headers: dict):
    response = client.post(
        "/api/v1/help/categories",
        headers=test_headers,
        json={
            "name": "Account Issues"
        }
    )
    assert response.status_code == 403


def test_get_categories(client: TestClient, admin_headers: dict):
    # Setup
    client.post("/api/v1/help/categories", headers=admin_headers, json={"name": "Test Cat 1"})
    
    response = client.get("/api/v1/help/categories")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1


def test_create_article_and_search(client: TestClient, admin_headers: dict):
    # Setup category
    cat_res = client.post("/api/v1/help/categories", headers=admin_headers, json={"name": "Search Test"})
    cat_id = cat_res.json()["data"]["id"]
    
    # Create article
    art_res = client.post(
        "/api/v1/help/articles",
        headers=admin_headers,
        json={
            "title": "How to reset password",
            "content": "Click the reset link in the email.",
            "category_id": cat_id,
            "is_published": True
        }
    )
    assert art_res.status_code == 201
    
    # Search article
    search_res = client.get("/api/v1/help/search?keyword=reset")
    assert search_res.status_code == 200
    data = search_res.json()
    assert data["meta"]["total"] >= 1
    assert data["data"][0]["title"] == "How to reset password"


def test_create_support_ticket(client: TestClient, test_headers: dict):
    response = client.post(
        "/api/v1/help/tickets",
        headers=test_headers,
        json={
            "title": "App keeps crashing",
            "description": "Whenever I open the dashboard, it crashes.",
            "module_name": "Dashboard",
            "priority": "High",
            "category": "Technical Issue"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "SUP" in data["data"]["ticket_number"]
    assert data["data"]["status"] == "Open"


def test_update_ticket_status_admin(client: TestClient, test_headers: dict, admin_headers: dict):
    # Setup ticket
    tick_res = client.post(
        "/api/v1/help/tickets",
        headers=test_headers,
        json={
            "title": "Issue",
            "description": "Desc",
            "module_name": "General",
            "priority": "Low",
            "category": "Other"
        }
    )
    ticket_id = tick_res.json()["data"]["id"]
    
    # Update status as admin
    response = client.put(
        f"/api/v1/help/tickets/{ticket_id}",
        headers=admin_headers,
        json={
            "status": "Resolved",
            "resolution_notes": "Fixed the bug."
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["status"] == "Resolved"
    assert data["data"]["resolution_notes"] == "Fixed the bug."


def test_submit_feedback(client: TestClient, test_headers: dict):
    response = client.post(
        "/api/v1/help/feedback",
        headers=test_headers,
        json={
            "rating": 5,
            "title": "Great app",
            "message": "Really enjoying the new UI."
        }
    )
    assert response.status_code == 201
    assert response.json()["data"]["rating"] == 5


def test_get_statistics_admin(client: TestClient, admin_headers: dict):
    response = client.get(
        "/api/v1/help/statistics",
        headers=admin_headers
    )
    assert response.status_code == 200
    assert "total_articles" in response.json()["data"]
