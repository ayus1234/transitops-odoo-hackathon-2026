"""
API endpoints for Help Center.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status, UploadFile, File, HTTPException
import os
import shutil
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user, get_current_active_user, RoleChecker
from app.models.user import User
from app.schemas.help_center import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    ArticleCreate, ArticleUpdate, ArticleResponse,
    TicketCreate, TicketUpdate, TicketStatusUpdate, TicketResponse,
    FeedbackCreate, FeedbackResponse, StatisticsResponse
)
from app.services.help_service import HelpService

router = APIRouter()


# --- Categories ---

@router.get("/categories", response_model=dict)
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Get all help categories."""
    service = HelpService(db)
    categories, total = service.get_categories(skip, limit, active_only)
    return {
        "success": True,
        "data": [CategoryResponse.model_validate(c).model_dump(mode="json") for c in categories],
        "meta": {"total": total, "skip": skip, "limit": limit}
    }


@router.post("/categories", response_model=dict, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RoleChecker(["System Admin"]))])
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new category (Admin only)."""
    service = HelpService(db)
    category = service.create_category(category_in)
    return {"success": True, "data": CategoryResponse.model_validate(category).model_dump(mode="json")}


@router.put("/categories/{category_id}", response_model=dict, dependencies=[Depends(RoleChecker(["System Admin"]))])
def update_category(
    category_id: UUID,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update a category (Admin only)."""
    service = HelpService(db)
    category = service.update_category(category_id, category_in)
    return {"success": True, "data": CategoryResponse.model_validate(category).model_dump(mode="json")}


@router.delete("/categories/{category_id}", dependencies=[Depends(RoleChecker(["System Admin"]))])
def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a category (Admin only)."""
    service = HelpService(db)
    return service.delete_category(category_id)


# --- Articles & Search ---

@router.get("/search", response_model=dict)
def search_help(
    keyword: Optional[str] = None,
    category: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search help articles."""
    service = HelpService(db)
    # Only show published in search
    articles, total = service.search_articles(skip, limit, category, is_published=True, search=keyword)
    return {
        "success": True,
        "data": [ArticleResponse.model_validate(a).model_dump(mode="json") for a in articles],
        "meta": {"total": total, "skip": skip, "limit": limit}
    }


@router.get("/articles", response_model=dict)
def get_articles(
    category_id: Optional[UUID] = None,
    is_published: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all help articles."""
    service = HelpService(db)
    articles, total = service.search_articles(skip, limit, category_id, is_published, is_featured)
    return {
        "success": True,
        "data": [ArticleResponse.model_validate(a).model_dump(mode="json") for a in articles],
        "meta": {"total": total, "skip": skip, "limit": limit}
    }


@router.get("/articles/popular", response_model=dict)
def get_popular_articles(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Get popular help articles by view count."""
    service = HelpService(db)
    articles = service.get_popular_articles(limit)
    return {"success": True, "data": [ArticleResponse.model_validate(a).model_dump(mode="json") for a in articles]}


@router.get("/articles/{article_id}", response_model=dict)
def get_article(
    article_id: UUID,
    db: Session = Depends(get_db)
):
    """Get article by ID."""
    service = HelpService(db)
    article = service.get_article(article_id)
    return {"success": True, "data": ArticleResponse.model_validate(article).model_dump(mode="json")}


@router.get("/articles/slug/{slug}", response_model=dict)
def get_article_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get article by slug."""
    service = HelpService(db)
    article = service.get_article_by_slug(slug)
    return {"success": True, "data": ArticleResponse.model_validate(article).model_dump(mode="json")}


@router.post("/articles", response_model=dict, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RoleChecker(["System Admin"]))])
def create_article(
    article_in: ArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new article (Admin only)."""
    service = HelpService(db)
    article = service.create_article(article_in, current_user)
    return {"success": True, "data": ArticleResponse.model_validate(article).model_dump(mode="json")}


@router.put("/articles/{article_id}", response_model=dict, dependencies=[Depends(RoleChecker(["System Admin"]))])
def update_article(
    article_id: UUID,
    article_in: ArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an article (Admin only)."""
    service = HelpService(db)
    article = service.update_article(article_id, article_in, current_user)
    return {"success": True, "data": ArticleResponse.model_validate(article).model_dump(mode="json")}


@router.delete("/articles/{article_id}", dependencies=[Depends(RoleChecker(["System Admin"]))])
def delete_article(
    article_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an article (Admin only)."""
    service = HelpService(db)
    return service.delete_article(article_id)


# --- Support Tickets ---

@router.get("/tickets", response_model=dict)
def get_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get support tickets. Users see their own; Admins see all."""
    service = HelpService(db)
    tickets, total = service.get_tickets(current_user, skip, limit, status, priority)
    return {
        "success": True,
        "data": [TicketResponse.model_validate(t).model_dump(mode="json") for t in tickets],
        "meta": {"total": total, "skip": skip, "limit": limit}
    }


@router.get("/tickets/search", response_model=dict)
def search_tickets(
    q: str = Query(..., description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Search support tickets."""
    service = HelpService(db)
    tickets, total = service.search_tickets(q, current_user, skip, limit)
    return {
        "success": True,
        "data": [TicketResponse.model_validate(t).model_dump(mode="json") for t in tickets],
        "meta": {"total": total, "skip": skip, "limit": limit}
    }


@router.get("/tickets/filter", response_model=dict)
def filter_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Filter support tickets."""
    service = HelpService(db)
    tickets, total = service.get_tickets(current_user, skip, limit, status, priority, category)
    return {
        "success": True,
        "data": [TicketResponse.model_validate(t).model_dump(mode="json") for t in tickets],
        "meta": {"total": total, "skip": skip, "limit": limit}
    }


@router.get("/tickets/{ticket_id}", response_model=dict)
def get_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get ticket by ID."""
    service = HelpService(db)
    ticket = service.get_ticket(ticket_id, current_user)
    return {"success": True, "data": TicketResponse.model_validate(ticket).model_dump(mode="json")}


@router.post("/tickets", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new support ticket."""
    service = HelpService(db)
    ticket = service.create_ticket(ticket_in, current_user)
    return {"success": True, "data": TicketResponse.model_validate(ticket).model_dump(mode="json")}


@router.put("/tickets/{ticket_id}", response_model=dict)
def update_ticket(
    ticket_id: UUID,
    ticket_in: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a ticket (Admin/Support only)."""
    service = HelpService(db)
    ticket = service.update_ticket(ticket_id, ticket_in, current_user)
    return {"success": True, "data": TicketResponse.model_validate(ticket).model_dump(mode="json")}


@router.post("/tickets/{ticket_id}/assign", response_model=dict)
def assign_ticket(
    ticket_id: UUID,
    assign_to_id: UUID = Query(..., description="User ID to assign the ticket to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Assign ticket to an agent."""
    service = HelpService(db)
    ticket = service.assign_ticket(ticket_id, assign_to_id, current_user)
    return {"success": True, "data": TicketResponse.model_validate(ticket).model_dump(mode="json")}


@router.post("/tickets/{ticket_id}/resolve", response_model=dict)
def resolve_ticket(
    ticket_id: UUID,
    resolution_notes: str = Query(..., description="Notes on how the ticket was resolved"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Resolve a support ticket."""
    service = HelpService(db)
    ticket = service.resolve_ticket(ticket_id, resolution_notes, current_user)
    return {"success": True, "data": TicketResponse.model_validate(ticket).model_dump(mode="json")}


@router.post("/tickets/{ticket_id}/close", response_model=dict)
def close_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Close a support ticket."""
    service = HelpService(db)
    ticket = service.close_ticket(ticket_id, current_user)
    return {"success": True, "data": TicketResponse.model_validate(ticket).model_dump(mode="json")}


@router.post("/tickets/upload", response_model=dict, status_code=status.HTTP_201_CREATED)
def upload_attachment(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a file attachment for a support ticket."""
    import uuid
    
    # Validate file type or size if necessary (optional)
    
    # Create unique filename
    ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join("uploads", unique_filename)
    
    # Save the file to disk
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
        
    # Return the static URL path
    return {"success": True, "data": {"url": f"/uploads/{unique_filename}"}}


# --- Feedback ---

@router.get("/feedback", response_model=dict, dependencies=[Depends(RoleChecker(["System Admin", "Management"]))])
def get_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all feedback (Admin/Management only)."""
    service = HelpService(db)
    feedback, total = service.get_feedback(skip, limit)
    return {
        "success": True,
        "data": [FeedbackResponse.model_validate(f).model_dump(mode="json") for f in feedback],
        "meta": {"total": total, "skip": skip, "limit": limit}
    }


@router.post("/feedback", response_model=dict, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit platform feedback."""
    service = HelpService(db)
    # Using get_current_user instead of active_user in case they are authenticated but inactive somehow, though active is better.
    # We will pass current_user directly.
    feedback = service.submit_feedback(feedback_in, current_user)
    return {"success": True, "data": FeedbackResponse.model_validate(feedback).model_dump(mode="json")}


@router.delete("/feedback/{feedback_id}", dependencies=[Depends(RoleChecker(["System Admin"]))])
def delete_feedback(
    feedback_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete feedback (Admin only)."""
    service = HelpService(db)
    return service.delete_feedback(feedback_id)


# --- Statistics ---

@router.get("/statistics", response_model=dict, dependencies=[Depends(RoleChecker(["System Admin", "Administrator", "Management"]))])
def get_statistics(
    db: Session = Depends(get_db)
):
    """Get help center statistics (Admin/Management only)."""
    service = HelpService(db)
    stats = service.get_statistics()
    return {"success": True, "data": stats}
