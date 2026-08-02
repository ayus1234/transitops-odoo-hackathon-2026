"""
Tests for Vendor / Service Management feature.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.role import Role
from app.models.user import User
from app.models.vendor import Vendor
from app.core.security import get_password_hash


@pytest.fixture
def vendor_user(db_session: Session) -> User:
    """Create Procurement Manager for Vendor testing."""
    role = Role(
        name="Procurement Manager VENDOR",
        permissions={"vendors": ["read", "create", "update", "delete"]}
    )
    db_session.add(role)
    db_session.commit()

    user = User(
        email="vendor_manager@transitops.com",
        password_hash=get_password_hash("password123"),
        first_name="Vendor",
        last_name="Manager",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def vendor_token(client: TestClient, vendor_user: User) -> str:
    """Get JWT token for vendor tester."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "vendor_manager@transitops.com",
            "password": "password123"
        }
    )
    return response.json()["access_token"]


def test_create_vendor_success(
    client: TestClient,
    vendor_token: str
):
    """Test successful vendor creation."""
    vendor_data = {
        "vendor_code": "VEND-001",
        "name": "AutoParts India Pvt Ltd",
        "contact_person": "Rajesh Kumar",
        "email": "contact@autopartsindia.com",
        "phone": "+919876500112",
        "categories": ["Parts", "Service"],
        "payment_terms": "Net 30",
        "tax_id": "GSTIN29ABCDE1234F1Z5",
        "rating": 4.8
    }

    response = client.post(
        "/api/v1/vendors",
        json=vendor_data,
        headers={"Authorization": f"Bearer {vendor_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["vendor_code"] == "VEND-001"
    assert data["name"] == "AutoParts India Pvt Ltd"
    assert data["categories"] == ["Parts", "Service"]
    assert float(data["rating"]) == 4.8


def test_create_vendor_duplicate_code(
    client: TestClient,
    db_session: Session,
    vendor_token: str
):
    """Test duplicate vendor code rejection."""
    v = Vendor(
        vendor_code="VEND-DUP-01",
        name="Existing Vendor"
    )
    db_session.add(v)
    db_session.commit()

    response = client.post(
        "/api/v1/vendors",
        json={
            "vendor_code": "VEND-DUP-01",
            "name": "Duplicate Vendor"
        },
        headers={"Authorization": f"Bearer {vendor_token}"}
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["error"]["message"].lower()


def test_list_and_search_vendors(
    client: TestClient,
    db_session: Session,
    vendor_token: str
):
    """Test listing vendors with search filter."""
    v = Vendor(
        vendor_code="VEND-SEARCH-01",
        name="AutoParts India Pvt Ltd",
        contact_person="Search Person"
    )
    db_session.add(v)
    db_session.commit()

    response = client.get(
        "/api/v1/vendors?search=AutoParts",
        headers={"Authorization": f"Bearer {vendor_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) >= 1
    assert data["data"][0]["name"] == "AutoParts India Pvt Ltd"


def test_get_vendor_scorecard(
    client: TestClient,
    db_session: Session,
    vendor_token: str
):
    """Test GET /vendors/{id}/scorecard endpoint."""
    v = Vendor(
        vendor_code="VEND-SCORE-01",
        name="Scorecard Vendor"
    )
    db_session.add(v)
    db_session.commit()

    response = client.get(
        f"/api/v1/vendors/{v.id}/scorecard",
        headers={"Authorization": f"Bearer {vendor_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "vendor" in data
    assert data["purchase_orders_count"] == 0
    assert float(data["total_spend"]) == 0.0


def test_update_vendor(
    client: TestClient,
    db_session: Session,
    vendor_token: str
):
    """Test updating vendor details."""
    v = Vendor(
        vendor_code="VEND-UPD-01",
        name="Old Vendor Name"
    )
    db_session.add(v)
    db_session.commit()

    response = client.put(
        f"/api/v1/vendors/{v.id}",
        json={"name": "New Vendor Name", "rating": 4.9},
        headers={"Authorization": f"Bearer {vendor_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Vendor Name"
    assert float(data["rating"]) == 4.9


def test_delete_vendor(
    client: TestClient,
    db_session: Session,
    vendor_token: str
):
    """Test deleting vendor."""
    v = Vendor(
        vendor_code="VEND-DEL-01",
        name="Delete Me Vendor"
    )
    db_session.add(v)
    db_session.commit()

    del_res = client.delete(
        f"/api/v1/vendors/{v.id}",
        headers={"Authorization": f"Bearer {vendor_token}"}
    )

    assert del_res.status_code == 200
    assert del_res.json()["success"] is True
