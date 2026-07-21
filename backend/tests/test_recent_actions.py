import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.quick_action import QuickAction

def create_mock_actions(db: Session):
    db.query(QuickAction).delete()
    db.add(QuickAction(name="register_vehicle", display_name="Register Vehicle", category="Vehicles", route="/vehicles/new", permission_resource="vehicles", permission_action="create"))
    db.commit()

def test_recent_actions_logged_and_limited(client: TestClient, admin_token_headers: dict, db_session: Session):
    create_mock_actions(db_session)
    action = db_session.query(QuickAction).filter_by(name="register_vehicle").first()
    
    # Execute multiple times
    client.post(f"/api/v1/quick-actions/{action.id}/execute", headers=admin_token_headers)
    client.post(f"/api/v1/quick-actions/{action.id}/execute", headers=admin_token_headers)
    
    response = client.get("/api/v1/quick-actions/recent", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    
    assert len(data) == 1
    assert data[0]["access_count"] == 2
    assert data[0]["action"]["name"] == "register_vehicle"

def test_export_recent_json(client: TestClient, admin_token_headers: dict, db_session: Session):
    create_mock_actions(db_session)
    action = db_session.query(QuickAction).filter_by(name="register_vehicle").first()
    client.post(f"/api/v1/quick-actions/{action.id}/execute", headers=admin_token_headers)
    
    response = client.get("/api/v1/quick-actions/export/recent?format=json", headers=admin_token_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert len(data) == 1
    assert data[0]["Action"] == "Register Vehicle"
