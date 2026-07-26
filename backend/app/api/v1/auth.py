"""
Authentication API endpoints.
"""
from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, DemoAccountInfo
from app.schemas.user import UserResponse
from app.schemas.common import SuccessResponse
from app.services.activity_service import activity_service
from app.schemas.activity import ActivityCreate
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum


router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Login endpoint to authenticate user and return JWT token.
    
    Args:
        credentials: Login credentials (email and password)
        db: Database session
        
    Returns:
        JWT token and user information
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        # We can't log the user_id since it's invalid, but we can log the attempt
        activity_service.log_activity(db, ActivityCreate(
            module=ModuleEnum.AUTHENTICATION,
            activity_type=ActivityTypeEnum.LOGIN,
            title="Failed Login Attempt",
            description=f"Invalid login attempt for email: {credentials.email}",
            severity=SeverityEnum.WARNING,
            status="Failed"
        ))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        activity_service.log_activity(db, ActivityCreate(
            module=ModuleEnum.AUTHENTICATION,
            activity_type=ActivityTypeEnum.LOGIN,
            title="Failed Login Attempt",
            description=f"Invalid password for email: {credentials.email}",
            severity=SeverityEnum.WARNING,
            status="Failed",
            user_id=str(user.id)
        ))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.name,
        },
        expires_delta=access_token_expires
    )
    
    # Log successful login
    activity_service.log_activity(db, ActivityCreate(
        module=ModuleEnum.AUTHENTICATION,
        activity_type=ActivityTypeEnum.LOGIN,
        title="User Login Successful",
        description="User successfully authenticated via API.",
        severity=SeverityEnum.INFO,
        status="Success",
        user_id=str(user.id)
    ))
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout", response_model=SuccessResponse)
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """
    Logout endpoint (JWT tokens are stateless, so this is mainly for client-side).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    # Log logout
    activity_service.log_activity(db, ActivityCreate(
        module=ModuleEnum.AUTHENTICATION,
        activity_type=ActivityTypeEnum.LOGOUT,
        title="User Logout",
        description="User session terminated.",
        severity=SeverityEnum.INFO,
        status="Success",
        user_id=str(current_user.id)
    ))

    return SuccessResponse(
        success=True,
        message="Logged out successfully"
    )


DEMO_ACCOUNTS_CATALOG: List[dict] = [
    {
        "role": "Super Admin",
        "email": "admin@transitops.com",
        "password": "admin123",
        "description": "Unrestricted administrative access across all enterprise ERP modules, user management, and system governance."
    },
    {
        "role": "Administrator",
        "email": "administrator@transitops.com",
        "password": "adminpass2026",
        "description": "Comprehensive administrative privileges for configuring roles, organization settings, and enterprise oversight."
    },
    {
        "role": "System Admin",
        "email": "sysadmin@transitops.com",
        "password": "sysadmin2026",
        "description": "Technical administrative control over system diagnostics, support center operations, and server configurations."
    },
    {
        "role": "Fleet Manager",
        "email": "fleet@transitops.com",
        "password": "fleet2026",
        "description": "Full fleet management capabilities including vehicle registry, driver assignments, trip tracking, and operational reports."
    },
    {
        "role": "Dispatcher",
        "email": "dispatcher@transitops.com",
        "password": "dispatch2026",
        "description": "Operational control over trip creation, route scheduling, driver assignments, and live dispatch monitoring."
    },
    {
        "role": "Maintenance Manager",
        "email": "maintenance@transitops.com",
        "password": "maint2026",
        "description": "Authority over vehicle servicing, repair schedules, maintenance approval workflows, and part inventory management."
    },
    {
        "role": "Technician",
        "email": "technician@transitops.com",
        "password": "tech2026",
        "description": "Field access to inspect vehicles, log repair notes, update task statuses, and monitor service checklists."
    },
    {
        "role": "Safety Officer",
        "email": "safety@transitops.com",
        "password": "safety2026",
        "description": "Focused access to driver safety scores, incident logs, compliance audits, and enterprise safety analytics."
    },
    {
        "role": "Financial Analyst",
        "email": "finance@transitops.com",
        "password": "finance123",
        "description": "Comprehensive financial insight across expenses, fuel budgeting, operational cost analytics, and accounting reports."
    },
    {
        "role": "Procurement Operations",
        "email": "procurement@transitops.com",
        "password": "procure2026",
        "description": "Management of inventory ordering, vendor purchase orders, spare parts requisition, and cost approvals."
    },
    {
        "role": "HR/Operations",
        "email": "hr@transitops.com",
        "password": "hr2026",
        "description": "Personnel management access for driver onboarding, profile updates, license verification, and HR records."
    },
    {
        "role": "Support Agent",
        "email": "support@transitops.com",
        "password": "support2026",
        "description": "Help center access to resolve user tickets, assist driver technical issues, and log support interactions."
    },
    {
        "role": "Driver",
        "email": "driver@transitops.com",
        "password": "driver2026",
        "description": "Driver portal access for viewing assigned trips, vehicle telemetry, navigation logs, and personal safety metrics."
    }
]


@router.get("/demo-accounts", response_model=List[DemoAccountInfo], tags=["Authentication"])
def list_demo_accounts() -> List[DemoAccountInfo]:
    """
    Retrieve dedicated role-based demo account credentials for hackathon testers and judges.
    
    Returns:
        List of demo account info containing role name, email, dedicated demo password, and role description.
    """
    return [DemoAccountInfo.model_validate(account) for account in DEMO_ACCOUNTS_CATALOG]
