"""
Pydantic schemas for the Help Center.
"""
from datetime import datetime
from typing import Optional, Any, Dict, List
from uuid import UUID
from pydantic import BaseModel, Field, constr


# --- Help Category Schemas ---

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    display_order: int = Field(default=0)
    is_active: bool = Field(default=True)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Help Article Schemas ---

class ArticleBase(BaseModel):
    title: str = Field(..., max_length=200)
    content: str
    summary: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    is_featured: bool = Field(default=False)
    is_published: bool = Field(default=True)


class ArticleCreate(ArticleBase):
    category_id: UUID


class ArticleUpdate(BaseModel):
    category_id: Optional[UUID] = None
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    is_featured: Optional[bool] = None
    is_published: Optional[bool] = None


class ArticleResponse(ArticleBase):
    id: UUID
    category_id: UUID
    slug: str
    view_count: int
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

    model_config = {"from_attributes": True}


# --- Support Ticket Schemas ---

class TicketBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: str
    module_name: str = Field(..., max_length=50)
    priority: str = Field(default="Medium", pattern="^(Low|Medium|High|Critical)$")
    category: str = Field(..., max_length=50)
    attachment_url: Optional[str] = Field(None, max_length=255)


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    module_name: Optional[str] = Field(None, max_length=50)
    priority: Optional[str] = Field(None, pattern="^(Low|Medium|High|Critical)$")
    category: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, pattern="^(Open|In Progress|Resolved|Closed)$")
    assigned_to: Optional[UUID] = None
    resolution_notes: Optional[str] = None
    attachment_url: Optional[str] = Field(None, max_length=255)


class TicketStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(Open|In Progress|Resolved|Closed)$")
    resolution_notes: Optional[str] = None


class TicketResponse(TicketBase):
    id: UUID
    ticket_number: str
    created_by: UUID
    status: str
    assigned_to: Optional[UUID] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Feedback Schemas ---

class FeedbackBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    message: Optional[str] = None
    page: Optional[str] = Field(None, max_length=255)


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackResponse(FeedbackBase):
    id: UUID
    user_id: Optional[UUID] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Statistics Schemas ---

class StatisticsResponse(BaseModel):
    total_articles: int
    total_categories: int
    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    total_feedback: int
    average_rating: float
