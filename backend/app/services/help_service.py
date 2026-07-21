"""
Help Center business logic service.
"""
import re
from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.activity_service import activity_service
from app.schemas.activity import ActivityCreate
from app.models.activity import ModuleEnum, ActivityTypeEnum, SeverityEnum
from app.schemas.help_center import (
    CategoryCreate, CategoryUpdate, 
    ArticleCreate, ArticleUpdate,
    TicketCreate, TicketUpdate, TicketStatusUpdate,
    FeedbackCreate
)
from app.repositories.help_repository import HelpRepository


class HelpService:
    """Service for Help Center business logic."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = HelpRepository(db)
        
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title."""
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[\s_-]+', '-', slug)
        slug = slug.strip('-')
        
        # Ensure uniqueness
        base_slug = slug
        counter = 1
        while self.repository.get_article_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        return slug

    # --- Categories ---
    
    def get_category(self, category_id: UUID):
        category = self.repository.get_category(category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return category
        
    def get_categories(self, skip: int = 0, limit: int = 100, active_only: bool = False):
        return self.repository.get_categories(skip, limit, active_only)
        
    def create_category(self, category_in: CategoryCreate):
        if self.repository.get_category_by_name(category_in.name):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")
        return self.repository.create_category(category_in.model_dump())
        
    def update_category(self, category_id: UUID, category_in: CategoryUpdate):
        category = self.get_category(category_id)
        
        if category_in.name and category_in.name.lower() != category.name.lower():
            if self.repository.get_category_by_name(category_in.name):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")
                
        update_data = category_in.model_dump(exclude_unset=True)
        return self.repository.update_category(category, update_data)
        
    def delete_category(self, category_id: UUID):
        category = self.get_category(category_id)
        self.repository.delete_category(category)
        return {"success": True, "message": "Category deleted"}


    # --- Articles ---
    
    def get_article(self, article_id: UUID):
        article = self.repository.get_article(article_id)
        if not article:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        return article
        
    def get_article_by_slug(self, slug: str):
        article = self.repository.get_article_by_slug(slug)
        if not article:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        
        # Increment view count automatically when fetched by slug (public view)
        self.repository.increment_view_count(article)
        return article
        
    def search_articles(self, skip: int = 0, limit: int = 20, category_id: Optional[UUID] = None, 
                        is_published: Optional[bool] = None, is_featured: Optional[bool] = None, search: Optional[str] = None):
        return self.repository.get_articles(skip, limit, category_id, is_published, is_featured, search)
        
    def get_popular_articles(self, limit: int = 5):
        return self.repository.get_popular_articles(limit)
        
    def create_article(self, article_in: ArticleCreate, current_user: User):
        self.get_category(article_in.category_id)  # validate category
        
        data = article_in.model_dump()
        data["slug"] = self._generate_slug(data["title"])
        data["created_by"] = current_user.id
        data["updated_by"] = current_user.id
        
        return self.repository.create_article(data)
        
    def update_article(self, article_id: UUID, article_in: ArticleUpdate, current_user: User):
        article = self.get_article(article_id)
        
        data = article_in.model_dump(exclude_unset=True)
        
        if "category_id" in data:
            self.get_category(data["category_id"])  # validate new category
            
        if "title" in data and data["title"] != article.title:
            data["slug"] = self._generate_slug(data["title"])
            
        data["updated_by"] = current_user.id
        
        return self.repository.update_article(article, data)
        
    def delete_article(self, article_id: UUID):
        article = self.get_article(article_id)
        self.repository.delete_article(article)
        return {"success": True, "message": "Article deleted"}


    # --- Support Tickets ---
    
    def get_ticket(self, ticket_id: UUID, current_user: User):
        ticket = self.repository.get_ticket(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
            
        # RBAC: Only Admin/Support, ticket owner, or Finance (if expense) can view it
        if current_user.role.name not in ["System Admin", "Support Agent"]:
            if current_user.role.name == "Finance" and ticket.category == "Expenses":
                pass
            elif ticket.created_by != current_user.id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this ticket")
            
        return ticket
        
    def get_tickets(self, current_user: User, skip: int = 0, limit: int = 20, 
                    status: Optional[str] = None, priority: Optional[str] = None, category: Optional[str] = None, assigned_to: Optional[UUID] = None):
        
        # Non-admins can only see their own tickets, unless Finance looking at Expenses
        created_by = None
        if current_user.role.name not in ["System Admin", "Support Agent"]:
            if current_user.role.name == "Finance":
                category = "Expenses" # Force filter to Expenses if Finance role
            else:
                created_by = current_user.id
                
        return self.repository.get_tickets(skip, limit, created_by, status, priority, category, assigned_to)
        
    def search_tickets(self, search: str, current_user: User, skip: int = 0, limit: int = 20):
        created_by = current_user.id if current_user.role.name not in ["System Admin", "Support Agent", "Finance"] else None
        
        tickets, total = self.repository.search_tickets(search, skip, limit, created_by)
        
        if current_user.role.name == "Finance":
            tickets = [t for t in tickets if t.category == "Expenses"]
            total = len(tickets)
            
        return tickets, total
        
    def create_ticket(self, ticket_in: TicketCreate, current_user: User):
        data = ticket_in.model_dump()
        data["created_by"] = current_user.id
        data["ticket_number"] = self.repository.generate_ticket_number()
        
        ticket = self.repository.create_ticket(data)
        
        activity_service.log_activity(self.db, ActivityCreate(
            module=ModuleEnum.HELP_CENTER,
            activity_type=ActivityTypeEnum.CREATED,
            title="Support Ticket Created",
            description=f"Ticket {ticket.ticket_number} was opened.",
            severity=SeverityEnum.INFO,
            status="Open",
            user_id=current_user.id
        ))
        
        from app.services.notification_service import NotificationService
        if ticket.priority == "Critical":
            # Notify admins of critical tickets
            NotificationService.notify_user(
                self.db,
                user_id=current_user.id,
                title="Critical Ticket Created",
                description=f"A critical support ticket {ticket.ticket_number} has been logged.",
                category="System",
                type="Critical",
                priority="Critical",
                module_name="Help Center",
                route=f"/help/tickets/{ticket.id}"
            )
            
        return ticket
        
    def update_ticket(self, ticket_id: UUID, ticket_in: TicketUpdate, current_user: User):
        ticket = self.get_ticket(ticket_id, current_user)
        
        if ticket.status == "Closed":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Closed tickets cannot be edited")
            
        if current_user.role.name not in ["System Admin", "Support Agent"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update ticket properties")
            
        data = ticket_in.model_dump(exclude_unset=True)
            
        return self.repository.update_ticket(ticket, data)
        
    def assign_ticket(self, ticket_id: UUID, assign_to_id: UUID, current_user: User):
        ticket = self.get_ticket(ticket_id, current_user)
        
        if current_user.role.name not in ["System Admin", "Support Agent"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to assign tickets")
            
        if ticket.status == "Closed":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot assign a closed ticket")
            
        ticket = self.repository.update_ticket(ticket, {"assigned_to": assign_to_id, "status": "In Progress"})
        
        activity_service.log_activity(self.db, ActivityCreate(
            module=ModuleEnum.HELP_CENTER,
            activity_type=ActivityTypeEnum.UPDATED,
            title="Ticket Assigned",
            description=f"Ticket {ticket.ticket_number} was assigned.",
            severity=SeverityEnum.INFO,
            status="In Progress",
            user_id=current_user.id
        ))
        
        from app.services.notification_service import NotificationService
        NotificationService.notify_user(
            self.db,
            title="Ticket Assigned",
            description=f"You have been assigned support ticket {ticket.ticket_number}.",
            category="System",
            type="Info",
            priority="Medium",
            module_name="Help Center",
            user_id=assign_to_id,
            route=f"/help/tickets/{ticket.id}"
        )
        
        return ticket

    def resolve_ticket(self, ticket_id: UUID, resolution_notes: str, current_user: User):
        ticket = self.get_ticket(ticket_id, current_user)
        
        if current_user.role.name not in ["System Admin", "Support Agent"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to resolve tickets")
            
        if ticket.status == "Closed":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot resolve a closed ticket")
            
        ticket = self.repository.update_ticket(ticket, {
            "status": "Resolved", 
            "resolution_notes": resolution_notes,
            "resolved_at": datetime.utcnow()
        })
        
        activity_service.log_activity(self.db, ActivityCreate(
            module=ModuleEnum.HELP_CENTER,
            activity_type=ActivityTypeEnum.COMPLETED,
            title="Ticket Resolved",
            description=f"Ticket {ticket.ticket_number} was resolved.",
            severity=SeverityEnum.SUCCESS,
            status="Resolved",
            user_id=current_user.id
        ))
        
        from app.services.notification_service import NotificationService
        NotificationService.notify_user(
            self.db,
            title="Support Ticket Resolved",
            description=f"Your support ticket {ticket.ticket_number} has been resolved.",
            category="System",
            type="Success",
            priority="Medium",
            module_name="Help Center",
            user_id=ticket.created_by,
            route=f"/help/tickets/{ticket.id}"
        )
        
        return ticket
        
    def close_ticket(self, ticket_id: UUID, current_user: User):
        ticket = self.get_ticket(ticket_id, current_user)
        
        if current_user.role.name not in ["System Admin", "Support Agent"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to close tickets")
            
        if ticket.status != "Resolved":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only resolved tickets can be closed")
            
        ticket = self.repository.update_ticket(ticket, {
            "status": "Closed", 
            "closed_at": datetime.utcnow()
        })
        
        activity_service.log_activity(self.db, ActivityCreate(
            module=ModuleEnum.HELP_CENTER,
            activity_type=ActivityTypeEnum.UPDATED,
            title="Ticket Closed",
            description=f"Ticket {ticket.ticket_number} was closed.",
            severity=SeverityEnum.INFO,
            status="Closed",
            user_id=current_user.id
        ))
        
        from app.services.notification_service import NotificationService
        NotificationService.notify_user(
            self.db,
            title="Support Ticket Closed",
            description=f"Your support ticket {ticket.ticket_number} has been closed.",
            category="System",
            type="Info",
            priority="Low",
            module_name="Help Center",
            user_id=ticket.created_by,
            route=f"/help/tickets/{ticket.id}"
        )
        
        return ticket


    # --- Feedback ---
    
    def get_feedback(self, skip: int = 0, limit: int = 50):
        return self.repository.get_feedback_list(skip, limit)
        
    def submit_feedback(self, feedback_in: FeedbackCreate, current_user: Optional[User] = None):
        data = feedback_in.model_dump()
        if current_user:
            data["user_id"] = current_user.id
            
        return self.repository.create_feedback(data)
        
    def delete_feedback(self, feedback_id: UUID):
        feedback, _ = self.repository.get_feedback_list(0, 1000) # Inefficient but ok for small feedback lists or we add a get_by_id
        target = next((f for f in feedback if f.id == feedback_id), None)
        if not target:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
            
        self.repository.delete_feedback(target)
        return {"success": True, "message": "Feedback deleted"}
        

    # --- Statistics ---
    
    def get_statistics(self):
        return self.repository.get_statistics()
