"""
Pydantic schemas package for request/response validation.
"""
from app.schemas.common import PaginationParams, PaginatedResponse
from app.schemas.auth import TokenResponse, LoginRequest
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.role import RoleBase, RoleResponse

__all__ = [
    "PaginationParams",
    "PaginatedResponse",
    "TokenResponse",
    "LoginRequest",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "RoleBase",
    "RoleResponse",
]
