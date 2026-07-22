import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.quick_action import QuickAction

def create_mock_actions(db: Session):
    db.query(QuickAction).delete()
    
    actions = [
        {"name": "register_vehicle", "display_name": "Register Vehicle", "category": "Vehicles", "route": "/vehicles/new", "permission_resource": "vehicles", "permission_action": "create"},
        {"name": "create_trip", "display_name": "Create Trip", "category": "Trips", "route": "/trips/new", "permission_resource": "trips", "permission_action": "create"},
        {"name": "view_trip_details", "display_name": "View Trip Details", "category": "Trips", "route": "/trips", "permission_resource": "trips", "permission_action": "read"},
    ]
    for act in actions:
        db.add(QuickAction(**act))
    db.commit()

def test_list_available_actions(client: TestClient, admin_token_headers: dict, db_session: Session):
    create_mock_actions(db_session)
    response = client.get("/api/v1/quick-actions", headers=admin_token_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert len(response.json()["data"]) == 3

def test_execute_action_success_and_logs(client: TestClient, admin_token_headers: dict, db_session: Session):
    create_mock_actions(db_session)
    action = db_session.query(QuickAction).filter_by(name="register_vehicle").first()
    
    response = client.post(f"/api/v1/quick-actions/{action.id}/execute", headers=admin_token_headers)
    assert response.status_code == 201
    assert response.json()["success"] is True
    assert response.json()["data"]["target_route"] == "/vehicles/new"
    
    # Check activity logs
    from app.models.activity import ActivityLog
    logs = db_session.query(ActivityLog).filter_by(title="Vehicle Registration Started").all()
    assert len(logs) == 1

def test_export_statistics(client: TestClient, admin_token_headers: dict, db_session: Session):
    create_mock_actions(db_session)
    response = client.get("/api/v1/quick-actions/export/statistics?format=csv", headers=admin_token_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "Metric,Value" in response.text
