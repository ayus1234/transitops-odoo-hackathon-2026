import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.quick_action import QuickAction

def create_mock_actions(db: Session):
    db.query(QuickAction).delete()
    db.add(QuickAction(name="register_vehicle", display_name="Register Vehicle", category="Vehicles", route="/vehicles/new", permission_resource="vehicles", permission_action="create"))
    db.add(QuickAction(name="create_trip", display_name="Create Trip", category="Trips", route="/trips/new", permission_resource="trips", permission_action="create"))
    db.commit()

def test_add_and_remove_favorite(client: TestClient, admin_token_headers: dict, db_session: Session):
    create_mock_actions(db_session)
    action = db_session.query(QuickAction).filter_by(name="register_vehicle").first()
    
    # Add favorite
    res = client.post("/api/v1/quick-actions/favorites/add", json={"action_id": str(action.id)}, headers=admin_token_headers)
    assert res.status_code == 200
    assert res.json()["data"]["is_favorite"] is True
    
    # Remove favorite
    res2 = client.post("/api/v1/quick-actions/favorites/remove", json={"action_id": str(action.id)}, headers=admin_token_headers)
    assert res2.status_code == 200
    assert res2.json()["data"]["is_favorite"] is False

def test_favorites_export_pdf(client: TestClient, admin_token_headers: dict, db_session: Session):
    create_mock_actions(db_session)
    action = db_session.query(QuickAction).filter_by(name="register_vehicle").first()
    client.post("/api/v1/quick-actions/favorites/add", json={"action_id": str(action.id)}, headers=admin_token_headers)
    
    response = client.get("/api/v1/quick-actions/export/favorites?format=pdf", headers=admin_token_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert b"PDF Export for favorites" in response.content
    assert b"Register Vehicle" in response.content
