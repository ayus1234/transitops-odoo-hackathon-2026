"""
Authentication API endpoints.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
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
            user_id=user.id
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
    user.last_login = datetime.utcnow()
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
        user_id=user.id
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
        user_id=current_user.id
    ))

    return SuccessResponse(
        success=True,
        message="Logged out successfully"
    )
