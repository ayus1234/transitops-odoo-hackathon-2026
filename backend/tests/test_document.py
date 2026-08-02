"""
Tests for Document & Contract Management feature.
"""
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.document import Document
from app.core.security import get_password_hash


@pytest.fixture
def doc_user(db_session: Session) -> User:
    """Create user for document testing."""
    role = Role(
        name="Fleet Manager DOC",
        permissions={"documents": ["read", "create", "update", "delete"]}
    )
    db_session.add(role)
    db_session.commit()

    user = User(
        email="doc_manager@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="Doc",
        last_name="Manager",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def doc_token(client: TestClient, doc_user: User) -> str:
    """Get JWT token for document tester."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "doc_manager@transitops.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def test_vehicle_for_doc(db_session: Session) -> Vehicle:
    """Create test vehicle for linking documents."""
    vehicle = Vehicle(
        registration_number="DOC-VEH-001",
        vehicle_name="Document Test Van",
        vehicle_type="Van",
        capacity_kg=1500.0,
        fuel_type="Diesel",
        current_odometer_km=1000.0,
        status="Available"
    )
    db_session.add(vehicle)
    db_session.commit()
    db_session.refresh(vehicle)
    return vehicle


def test_create_document_success(
    client: TestClient,
    doc_token: str,
    test_vehicle_for_doc: Vehicle
):
    """Test successful document creation."""
    doc_data = {
        "document_type": "insurance",
        "document_number": "POL-99887766",
        "title": "Comprehensive Vehicle Insurance 2026",
        "issue_date": "2026-01-01",
        "expiry_date": "2027-01-01",
        "issuer": "National Insurance Co",
        "vehicle_id": str(test_vehicle_for_doc.id),
        "notes": "Annual policy renewal"
    }

    response = client.post(
        "/api/v1/documents",
        json=doc_data,
        headers={"Authorization": f"Bearer {doc_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["document_type"] == "insurance"
    assert data["document_number"] == "POL-99887766"
    assert data["status"] == "Active"
    assert data["verification_state"] == "Unverified"
    assert data["vehicle_id"] == str(test_vehicle_for_doc.id)


def test_create_document_invalid_type(
    client: TestClient,
    doc_token: str
):
    """Test creating document with invalid type."""
    doc_data = {
        "document_type": "invalid_type",
        "title": "Bad Doc"
    }

    response = client.post(
        "/api/v1/documents",
        json=doc_data,
        headers={"Authorization": f"Bearer {doc_token}"}
    )

    assert response.status_code == 422


def test_list_and_filter_documents(
    client: TestClient,
    doc_token: str,
    test_vehicle_for_doc: Vehicle
):
    """Test listing documents with vehicle_id filter."""
    # Create doc linked to vehicle
    client.post(
        "/api/v1/documents",
        json={
            "document_type": "registration",
            "title": "Vehicle Registration Certificate",
            "vehicle_id": str(test_vehicle_for_doc.id)
        },
        headers={"Authorization": f"Bearer {doc_token}"}
    )

    response = client.get(
        f"/api/v1/documents?vehicle_id={test_vehicle_for_doc.id}",
        headers={"Authorization": f"Bearer {doc_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1
    assert data["data"][0]["title"] == "Vehicle Registration Certificate"


def test_verify_document(
    client: TestClient,
    doc_token: str,
    test_vehicle_for_doc: Vehicle
):
    """Test document verification endpoint."""
    # Create doc
    res = client.post(
        "/api/v1/documents",
        json={
            "document_type": "fitness",
            "title": "Fitness Certificate",
            "vehicle_id": str(test_vehicle_for_doc.id)
        },
        headers={"Authorization": f"Bearer {doc_token}"}
    )
    doc_id = res.json()["id"]

    # Verify doc
    verify_res = client.patch(
        f"/api/v1/documents/{doc_id}/verify",
        json={
            "verification_state": "Verified",
            "notes": "Verified against RTO portal"
        },
        headers={"Authorization": f"Bearer {doc_token}"}
    )

    assert verify_res.status_code == 200
    verified_data = verify_res.json()
    assert verified_data["verification_state"] == "Verified"
    assert verified_data["verified_by"] is not None


def test_expiring_documents_feed(
    client: TestClient,
    doc_token: str
):
    """Test GET /documents/expiring feed."""
    expiring_soon = (date.today() + timedelta(days=15)).strftime("%Y-%m-%d")

    client.post(
        "/api/v1/documents",
        json={
            "document_type": "permit",
            "title": "National Route Permit",
            "expiry_date": expiring_soon
        },
        headers={"Authorization": f"Bearer {doc_token}"}
    )

    response = client.get(
        "/api/v1/documents/expiring?days=30",
        headers={"Authorization": f"Bearer {doc_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(d["title"] == "National Route Permit" for d in data)


def test_expired_document_status_auto_update(
    client: TestClient,
    doc_token: str
):
    """Test that a document with a past expiry date automatically gets status 'Expired'."""
    past_date = (date.today() - timedelta(days=5)).strftime("%Y-%m-%d")

    res = client.post(
        "/api/v1/documents",
        json={
            "document_type": "pollution",
            "title": "Expired Emission Certificate",
            "expiry_date": past_date
        },
        headers={"Authorization": f"Bearer {doc_token}"}
    )

    assert res.status_code == 201
    doc_id = res.json()["id"]

    # Fetch document and verify status turned Expired
    fetch_res = client.get(
        f"/api/v1/documents/{doc_id}",
        headers={"Authorization": f"Bearer {doc_token}"}
    )

    assert fetch_res.status_code == 200
    assert fetch_res.json()["status"] == "Expired"
    assert fetch_res.json()["is_expired"] is True


def test_delete_document(
    client: TestClient,
    doc_token: str
):
    """Test deleting a document."""
    res = client.post(
        "/api/v1/documents",
        json={
            "document_type": "other",
            "title": "Temporary Note Doc"
        },
        headers={"Authorization": f"Bearer {doc_token}"}
    )
    doc_id = res.json()["id"]

    del_res = client.delete(
        f"/api/v1/documents/{doc_id}",
        headers={"Authorization": f"Bearer {doc_token}"}
    )

    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # Confirm 400 not found (handled by global error handler)
    get_res = client.get(
        f"/api/v1/documents/{doc_id}",
        headers={"Authorization": f"Bearer {doc_token}"}
    )
    assert get_res.status_code == 400
