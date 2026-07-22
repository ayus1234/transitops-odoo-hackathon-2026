import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.quick_action import QuickAction

def create_mock_actions(db: Session):
    db.query(QuickAction).delete()
    # Driver does not have "create" on "vehicles", but does have "read" on "trips" (see conftest.py)
    db.add(QuickAction(name="register_vehicle", display_name="Register Vehicle", category="Vehicles", route="/vehicles/new", permission_resource="vehicles", permission_action="create"))
    db.add(QuickAction(name="view_trip_details", display_name="View Trip Details", category="Trips", route="/trips", permission_resource="trips", permission_action="read"))
    db.commit()

def test_permissions_grouping(client: TestClient, driver_token_headers: dict, db_session: Session):
    create_mock_actions(db_session)
    response = client.get("/api/v1/quick-actions/permissions", headers=driver_token_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    
    # Driver should be allowed to view trip details, but restricted from registering vehicle
    allowed_names = [a["name"] for a in data["allowed"]]
    restricted_names = [a["name"] for a in data["restricted"]]
    
    assert "view_trip_details" in allowed_names
    assert "register_vehicle" in restricted_names

def test_execute_permission_denied_logs_notification(client: TestClient, driver_token_headers: dict, db_session: Session):
    create_mock_actions(db_session)
    action = db_session.query(QuickAction).filter_by(name="register_vehicle").first()
    
    response = client.post(f"/api/v1/quick-actions/{action.id}/execute", headers=driver_token_headers)
    assert response.status_code == 403
    
    # Verify Activity Log
    from app.models.activity import ActivityLog
    logs = db_session.query(ActivityLog).filter_by(title="Permission Denied").all()
    assert len(logs) == 1
    assert "without proper permissions" in logs[0].description
    
    # Verify Notification
    from app.models.notification import Notification
    notifs = db_session.query(Notification).filter_by(title="Permission Denied").all()
    assert len(notifs) == 1
    assert "You do not have permission" in notifs[0].description
