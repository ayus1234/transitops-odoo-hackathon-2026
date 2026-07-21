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


# Use a Postgres test database
TEST_DATABASE_URL = "postgresql+psycopg2://postgres:1234@localhost:5432/transitops_test"

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
    """Create a new database session for a test with nested transactions."""
    connection = db_engine.connect()
    transaction = connection.begin()
    
    # Use nested transaction so test commits don't actually commit to DB
    session = TestingSessionLocal(bind=connection, join_transaction_mode="create_savepoint")
    
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

@pytest.fixture(scope="function")
def admin_token_headers(client: TestClient, db_session: Session) -> dict:
    """Create authentication headers for a System Admin."""
    from app.models.role import Role
    from app.models.user import User
    from app.core.security import get_password_hash
    
    role = Role(name="System Admin", permissions={"all": ["read", "create", "update", "delete"]})
    db_session.add(role)
    db_session.commit()
    
    user = User(
        email="admin@transitops.com", password_hash=get_password_hash("testpass123"),
        first_name="Admin", last_name="User", role_id=role.id, is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    response = client.post("/api/v1/auth/login", json={"email": "admin@transitops.com", "password": "testpass123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

@pytest.fixture(scope="function")
def driver_token_headers(client: TestClient, db_session: Session) -> dict:
    """Create authentication headers for a Driver."""
    from app.models.role import Role
    from app.models.user import User
    from app.core.security import get_password_hash
    
    role = Role(name="Driver", permissions={"trips": ["read"]})
    db_session.add(role)
    db_session.commit()
    
    user = User(
        email="driver@transitops.com", password_hash=get_password_hash("testpass123"),
        first_name="Driver", last_name="User", role_id=role.id, is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    response = client.post("/api/v1/auth/login", json={"email": "driver@transitops.com", "password": "testpass123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

# Removed duplicate fixtures
