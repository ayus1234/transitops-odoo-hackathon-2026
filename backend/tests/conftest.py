"""
Pytest configuration and fixtures for testing.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings


# Test database URL (use a separate test database)
TEST_DATABASE_URL = "postgresql://postgres:password@localhost:5432/transitops_test"

# Create test engine
test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a new database session for a test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(client: TestClient, db_session: Session) -> dict:
    """Create authentication headers with valid JWT token."""
    from app.models.role import Role
    from app.models.user import User
    from app.core.security import get_password_hash
    
    # Create test role
    role = Role(
        name="Test Role",
        permissions={"all": ["read", "create", "update", "delete"]}
    )
    db_session.add(role)
    db_session.commit()
    
    # Create test user
    user = User(
        email="test@transitops.com",
        password_hash=get_password_hash("testpass123"),
        first_name="Test",
        last_name="User",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Login to get token
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@transitops.com", "password": "testpass123"}
    )
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
