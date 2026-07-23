"""
Main FastAPI application entry point.
"""
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

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Smart Transport Operations Platform - ERP for Fleet Management",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

import tempfile
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


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    Initialize database tables if they don't exist.
    """
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    
    # Create tables (only for development, use Alembic for production)
    if settings.ENVIRONMENT == "development":
        # Base.metadata.create_all(bind=engine)
        print("Database tables created")
        
    # Start Live Simulation Engine (only if not on Vercel/Lambda)
    # Disabled so local and Vercel stay perfectly identical
    # if not os.environ.get("VERCEL"):
    #     asyncio.create_task(start_demo_engine())
    # else:
    print("Demo Engine completely disabled to ensure 100% identical data.")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event.
    """
    print(f"Shutting down {settings.APP_NAME}")

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
