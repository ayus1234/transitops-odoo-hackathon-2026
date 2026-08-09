"""
Database configuration and session management.
Uses SQLAlchemy 2.0 with PostgreSQL.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings


import ssl

# Create SSL context for remote PostgreSQL connections (Neon, Supabase, etc.)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

connect_args = {}
# Use SSL if this is a remote PostgreSQL database (not sqlite, not localhost)
if "sqlite" not in settings.DATABASE_URL and "localhost" not in settings.DATABASE_URL and "127.0.0.1" not in settings.DATABASE_URL:
    connect_args["ssl_context"] = ssl_context

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    poolclass=NullPool if settings.ENVIRONMENT == "testing" else None,
    connect_args=connect_args
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


_db_initialized = False

def ensure_database_initialized() -> None:
    """Ensure database tables and demo seed users exist on demand."""
    global _db_initialized
    if _db_initialized:
        return
    try:
        # Import all models to ensure registration
        import app.models  # noqa: F401
        Base.metadata.create_all(bind=engine)
        
        from app.models.user import User
        from app.models.role import Role
        from app.api.v1.auth import DEMO_ACCOUNTS_CATALOG, get_default_permissions_for_role
        from app.core.security import get_password_hash
        
        db = SessionLocal()
        user_exists = db.query(User).first()
        if not user_exists:
            for acct in DEMO_ACCOUNTS_CATALOG:
                role_obj = db.query(Role).filter(Role.name == acct["role"]).first()
                if not role_obj:
                    role_obj = Role(
                        name=acct["role"],
                        description=f"{acct['role']} Role",
                        permissions=get_default_permissions_for_role(acct["role"])
                    )
                    db.add(role_obj)
                    db.flush()
                user_obj = User(
                    email=acct["email"],
                    hashed_password=get_password_hash(acct["password"]),
                    full_name=acct["full_name"],
                    role_id=role_obj.id,
                    is_active=True,
                    is_superuser=(acct["role"] in ["Super Admin", "Administrator"])
                )
                db.add(user_obj)
            db.commit()
        db.close()
        _db_initialized = True
    except Exception as e:
        print(f"Database auto-init notice: {e}")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Automatically ensures tables and seed users exist before returning session.
    """
    ensure_database_initialized()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.
    Creates all tables defined in models.
    """
    # Import models to ensure they are registered with Base.metadata
    from app.models.inventory import InventoryItem, ProcurementRequest, PurchaseOrder, InventoryHistory
    
    Base.metadata.create_all(bind=engine)
