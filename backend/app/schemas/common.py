"""
Common schemas used across the application.
"""
from typing import Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


# Generic type for paginated responses
T = TypeVar("T")


class PaginationParams(BaseModel):
    """
    Query parameters for pagination.
    """
    page: int = Field(default=1, ge=1, description="Page number (starts at 1)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit for database query."""
        return self.page_size


class PaginationMeta(BaseModel):
    """
    Pagination metadata for responses.
    """
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response wrapper.
    """
    success: bool = Field(default=True)
    data: List[T]
    pagination: PaginationMeta
    
    model_config = ConfigDict(from_attributes=True)


class SuccessResponse(BaseModel):
    """
    Standard success response.
    """
    success: bool = Field(default=True)
    message: str
    data: Optional[Any] = None
    
    model_config = ConfigDict(from_attributes=True)


class ErrorDetail(BaseModel):
    """
    Error detail structure.
    """
    code: str
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """
    Standard error response.
    """
    success: bool = Field(default=False)
    error: ErrorDetail
    
    model_config = ConfigDict(from_attributes=True)
