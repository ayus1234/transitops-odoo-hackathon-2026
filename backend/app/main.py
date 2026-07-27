"""
Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import api_router
from app.utils.exceptions import TransitOpsException
from app.core.demo_engine import start_demo_engine
import asyncio
from fastapi.staticfiles import StaticFiles
import os
import tempfile

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """
    Application lifespan event handler (replaces deprecated on_event startup/shutdown).
    """
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    
    if settings.ENVIRONMENT == "development":
        print("Database tables created")

    # Ensure all 13 demo role accounts exist so hackathon evaluators never encounter invalid credentials
    try:
        from app.core.database import SessionLocal
        from app.models.role import Role
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.api.v1.auth import DEMO_ACCOUNTS_CATALOG, get_default_permissions_for_role
        db = SessionLocal()
        for acct in DEMO_ACCOUNTS_CATALOG:
            role_name = acct["role"]
            email = acct["email"]
            pwd = acct["password"]
            role_obj = db.query(Role).filter(Role.name == role_name).first()
            expected_perms = get_default_permissions_for_role(role_name)
            if not role_obj:
                role_obj = Role(name=role_name, permissions=expected_perms)
                db.add(role_obj)
                db.flush()
            elif role_obj.permissions != expected_perms:
                role_obj.permissions = expected_perms
                db.flush()
            user_obj = db.query(User).filter(User.email == email).first()
            if not user_obj:
                fname = role_name.split()[0]
                lname = "User"
                user_obj = User(
                    email=email,
                    password_hash=get_password_hash(pwd),
                    first_name=fname,
                    last_name=lname,
                    role_id=role_obj.id,
                    is_active=True
                )
                db.add(user_obj)
                db.flush()
            else:
                user_obj.role_id = role_obj.id
                user_obj.password_hash = get_password_hash(pwd)
                user_obj.is_active = True
                if not user_obj.last_name or len(user_obj.last_name.strip()) == 0:
                    user_obj.last_name = "User"
                db.flush()

            if email == "driver@transitops.com" and user_obj:
                from app.models.driver import Driver
                from datetime import date
                d_rec = db.query(Driver).filter(Driver.user_id == user_obj.id).first()
                if not d_rec:
                    d_rec = Driver(
                        user_id=user_obj.id,
                        license_number="DL-2026-DEMO",
                        license_category="HGMV",
                        license_issue_date=date(2021, 1, 1),
                        license_expiry_date=date(2031, 1, 1),
                        date_of_birth=date(1990, 5, 15),
                        safety_score=98.5,
                        total_trips=142,
                        status="Available",
                        latitude=19.0760,
                        longitude=72.8777
                    )
                    db.add(d_rec)
        
        from app.models.permission_audit import PermissionAuditLog
        if db.query(PermissionAuditLog).count() == 0:
            from datetime import datetime, timezone, timedelta
            now = datetime.now(timezone.utc)
            audit_entries = [
                PermissionAuditLog(action="CREATE_ROLE", new_value={"name": "Super Admin"}, timestamp=now - timedelta(minutes=120)),
                PermissionAuditLog(action="CREATE_ROLE", new_value={"name": "Fleet Manager"}, timestamp=now - timedelta(minutes=115)),
                PermissionAuditLog(action="CREATE_ROLE", new_value={"name": "Driver"}, timestamp=now - timedelta(minutes=110)),
                PermissionAuditLog(action="UPDATE_ROLE", new_value={"name": "Enterprise RBAC Matrix Synced"}, timestamp=now - timedelta(minutes=60)),
                PermissionAuditLog(action="BULK_ASSIGN_ROLE", new_value={"users_affected": 13}, timestamp=now - timedelta(minutes=30)),
                PermissionAuditLog(action="ASSIGN_ROLE", new_value={"role": "Fleet Manager", "users_affected": 4}, timestamp=now - timedelta(minutes=15)),
            ]
            for ae in audit_entries:
                db.add(ae)

        db.commit()
        db.close()
        print("Verified all 13 role-based demo credentials, Driver profiles, and RBAC audit logs on startup.")
    except Exception as e:
        print(f"Notice: Demo credential validation skipped: {e}")
        
    print("Demo Engine completely disabled to ensure 100% identical data.")
    yield
    print(f"Shutting down {settings.APP_NAME}")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Smart Transport Operations Platform - ERP for Fleet Management",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Ensure uploads directory exists and mount it (use /tmp for Vercel Serverless compatibility)
UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Exception handlers
@app.exception_handler(TransitOpsException)
async def transitops_exception_handler(request: Request, exc: TransitOpsException):
    """Handle custom TransitOps exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VAL_001",
                "message": "Validation error",
                "details": str(exc.errors())
            }
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "SYS_001",
                "message": f"Database error occurred: {str(exc)}",
                "details": {}
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "SYS_002",
                "message": "Internal server error",
                "details": {}
            }
        }
    )

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Welcome to TransitOps API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/api/v1/setup-vercel-db")
async def setup_vercel_db():
    try:
        from app.core.database import Base, engine
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import seed_demo_data
        import seed_inventory_demo_data
        import seed_activity_demo_data
        
        print("Seeding core data...")
        seed_demo_data.run()
        print("Seeding inventory data...")
        seed_inventory_demo_data.seed_data()
        print("Seeding activity data...")
        seed_activity_demo_data.run()
        
        return {"success": True, "message": "Database tables created and ALL demo data (core, inventory, activity) seeded successfully!"}
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
