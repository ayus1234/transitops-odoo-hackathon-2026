"""
Authentication schemas for login and token management.
"""
from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    """
    Schema for login request.
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """
    Schema for JWT token response.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")


class DemoAccountInfo(BaseModel):
    """
    Schema for demo account details provided for hackathon testing and demo login.
    """
    role: str = Field(..., description="Role name associated with the demo account")
    email: EmailStr = Field(..., description="Demo account email address")
    password: str = Field(..., description="Dedicated demo password for population in login UI")
    description: str = Field(..., description="Brief summary of the role's permissions and use case")
