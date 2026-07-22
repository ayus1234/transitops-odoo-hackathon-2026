import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from app.models.notification import Notification
from app.models.user import User


def test_get_notifications(client: TestClient, auth_headers: dict, db_session: Session):
    test_user = db_session.query(User).filter_by(email="test@transitops.com").first()
    
    notif = Notification(
        user_id=test_user.id,
        title="Test Notification",
        description="This is a test enterprise notification",
        type="Info",
        priority="Low",
        category="System",
        module_name="System",
        severity="Info",
        route="/",
        icon_name="Activity"
    )
    db_session.add(notif)
    db_session.commit()

    response = client.get("/api/v1/notifications/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["total"] >= 1
    assert any(n["title"] == "Test Notification" for n in data["data"])


def test_mark_notification_read(client: TestClient, auth_headers: dict, db_session: Session):
    test_user = db_session.query(User).filter_by(email="test@transitops.com").first()
    notif = Notification(
        user_id=test_user.id,
        title="To be read",
        description="Read me",
        type="Info",
        priority="Low",
        category="System",
        module_name="System",
        severity="Info"
    )
    db_session.add(notif)
    db_session.commit()
    db_session.refresh(notif)

    response = client.patch(f"/api/v1/notifications/{notif.id}/read", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_read"] is True


def test_mark_all_read(client: TestClient, auth_headers: dict, db_session: Session):
    test_user = db_session.query(User).filter_by(email="test@transitops.com").first()
    for _ in range(2):
        notif = Notification(
            user_id=test_user.id,
            title="Unread",
            description="Unread",
            type="Info",
            priority="Low",
            category="System",
            module_name="System",
            severity="Info"
        )
        db_session.add(notif)
    db_session.commit()

    response = client.post("/api/v1/notifications/mark-all-read", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["count"] >= 2


def test_archive_notification(client: TestClient, auth_headers: dict, db_session: Session):
    test_user = db_session.query(User).filter_by(email="test@transitops.com").first()
    notif = Notification(
        user_id=test_user.id,
        title="To be archived",
        description="Archive me",
        type="Info",
        priority="Low",
        category="System",
        module_name="System",
        severity="Info"
    )
    db_session.add(notif)
    db_session.commit()
    db_session.refresh(notif)

    response = client.patch(f"/api/v1/notifications/{notif.id}/archive", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["is_archived"] is True
    
    response2 = client.post(f"/api/v1/notifications/{notif.id}/unarchive", headers=auth_headers)
    assert response2.status_code == 200
    assert response2.json()["is_archived"] is False


def test_execute_notification(client: TestClient, auth_headers: dict, db_session: Session):
    test_user = db_session.query(User).filter_by(email="test@transitops.com").first()
    notif = Notification(
        user_id=test_user.id,
        title="Execute me",
        description="Execute",
        type="Info",
        priority="Low",
        category="System",
        module_name="System",
        severity="Info",
        route="/test-route"
    )
    db_session.add(notif)
    db_session.commit()
    db_session.refresh(notif)

    response = client.post(f"/api/v1/notifications/{notif.id}/execute", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["route"] == "/test-route"


def test_notification_search(client: TestClient, auth_headers: dict, db_session: Session):
    test_user = db_session.query(User).filter_by(email="test@transitops.com").first()
    notif = Notification(
        user_id=test_user.id,
        title="Find Me Enterprise",
        description="Searchable text",
        type="Info",
        priority="Low",
        category="System",
        module_name="System",
        severity="Info"
    )
    db_session.add(notif)
    db_session.commit()

    response = client.get("/api/v1/notifications/search?q=Enterprise", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert any(n["title"] == "Find Me Enterprise" for n in data["data"])


def test_notification_statistics(client: TestClient, auth_headers: dict):
    response = client.get("/api/v1/notifications/statistics", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "unread" in data
    assert "by_priority" in data
