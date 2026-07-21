"""
Help Center repository for database operations.
"""
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime, date
from sqlalchemy import func, or_, and_, desc
from sqlalchemy.orm import Session, joinedload

from app.models.help_center import HelpCategory, HelpArticle, SupportTicket, Feedback


class HelpRepository:
    """Repository for help center database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # --- Categories ---
    
    def get_category(self, category_id: UUID) -> Optional[HelpCategory]:
        return self.db.query(HelpCategory).filter(HelpCategory.id == category_id).first()
        
    def get_category_by_name(self, name: str) -> Optional[HelpCategory]:
        return self.db.query(HelpCategory).filter(func.lower(HelpCategory.name) == name.lower()).first()
    
    def get_categories(self, skip: int = 0, limit: int = 100, active_only: bool = False) -> Tuple[List[HelpCategory], int]:
        query = self.db.query(HelpCategory)
        if active_only:
            query = query.filter(HelpCategory.is_active == True)
            
        total = query.count()
        categories = query.order_by(HelpCategory.display_order.asc(), HelpCategory.name.asc()).offset(skip).limit(limit).all()
        return categories, total
        
    def create_category(self, data: dict) -> HelpCategory:
        category = HelpCategory(**data)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category
        
    def update_category(self, category: HelpCategory, data: dict) -> HelpCategory:
        for key, value in data.items():
            setattr(category, key, value)
        self.db.commit()
        self.db.refresh(category)
        return category
        
    def delete_category(self, category: HelpCategory) -> None:
        self.db.delete(category)
        self.db.commit()


    # --- Articles ---
    
    def get_article(self, article_id: UUID) -> Optional[HelpArticle]:
        return self.db.query(HelpArticle).options(joinedload(HelpArticle.category)).filter(HelpArticle.id == article_id).first()
        
    def get_article_by_slug(self, slug: str) -> Optional[HelpArticle]:
        return self.db.query(HelpArticle).options(joinedload(HelpArticle.category)).filter(HelpArticle.slug == slug).first()
        
    def get_articles(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        category_id: Optional[UUID] = None,
        is_published: Optional[bool] = None,
        is_featured: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[HelpArticle], int]:
        query = self.db.query(HelpArticle).options(joinedload(HelpArticle.category))
        
        if category_id:
            query = query.filter(HelpArticle.category_id == category_id)
        if is_published is not None:
            query = query.filter(HelpArticle.is_published == is_published)
        if is_featured is not None:
            query = query.filter(HelpArticle.is_featured == is_featured)
            
        if search:
            search_term = f"%{search}%"
            from sqlalchemy import String
            query = query.join(HelpCategory).filter(
                or_(
                    HelpArticle.title.ilike(search_term),
                    HelpArticle.summary.ilike(search_term),
                    HelpArticle.content.ilike(search_term),
                    HelpCategory.name.ilike(search_term),
                    HelpArticle.tags.cast(String).ilike(search_term)
                )
            )
            
        total = query.count()
        articles = query.order_by(desc(HelpArticle.created_at)).offset(skip).limit(limit).all()
        return articles, total
        
    def get_popular_articles(self, limit: int = 5) -> List[HelpArticle]:
        return self.db.query(HelpArticle).filter(HelpArticle.is_published == True)\
            .order_by(desc(HelpArticle.view_count)).limit(limit).all()
            
    def increment_view_count(self, article: HelpArticle) -> None:
        article.view_count += 1
        self.db.commit()
        
    def create_article(self, data: dict) -> HelpArticle:
        article = HelpArticle(**data)
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article
        
    def update_article(self, article: HelpArticle, data: dict) -> HelpArticle:
        for key, value in data.items():
            setattr(article, key, value)
        self.db.commit()
        self.db.refresh(article)
        return article
        
    def delete_article(self, article: HelpArticle) -> None:
        self.db.delete(article)
        self.db.commit()


    # --- Support Tickets ---
    
    def get_ticket(self, ticket_id: UUID) -> Optional[SupportTicket]:
        return self.db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        
    def get_tickets(
        self,
        skip: int = 0,
        limit: int = 20,
        created_by: Optional[UUID] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        assigned_to: Optional[UUID] = None
    ) -> Tuple[List[SupportTicket], int]:
        query = self.db.query(SupportTicket)
        
        if created_by:
            query = query.filter(SupportTicket.created_by == created_by)
        if status:
            query = query.filter(SupportTicket.status == status)
        if priority:
            query = query.filter(SupportTicket.priority == priority)
        if category:
            query = query.filter(SupportTicket.category == category)
        if assigned_to:
            query = query.filter(SupportTicket.assigned_to == assigned_to)
            
        total = query.count()
        tickets = query.order_by(desc(SupportTicket.created_at)).offset(skip).limit(limit).all()
        return tickets, total
        
    def search_tickets(self, search: str, skip: int = 0, limit: int = 20, created_by: Optional[UUID] = None) -> Tuple[List[SupportTicket], int]:
        query = self.db.query(SupportTicket)
        if created_by:
            query = query.filter(SupportTicket.created_by == created_by)
            
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                SupportTicket.title.ilike(search_term),
                SupportTicket.description.ilike(search_term),
                SupportTicket.ticket_number.ilike(search_term),
                SupportTicket.module_name.ilike(search_term)
            )
        )
        total = query.count()
        tickets = query.order_by(desc(SupportTicket.created_at)).offset(skip).limit(limit).all()
        return tickets, total
        
    def create_ticket(self, data: dict) -> SupportTicket:
        ticket = SupportTicket(**data)
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
        
    def update_ticket(self, ticket: SupportTicket, data: dict) -> SupportTicket:
        for key, value in data.items():
            setattr(ticket, key, value)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
        
    def generate_ticket_number(self) -> str:
        """Generate next ticket number (SUP-YYYY-NNNNN)."""
        year = date.today().year
        prefix = f"SUP-{year}-"
        
        last_ticket = self.db.query(SupportTicket).filter(
            SupportTicket.ticket_number.like(f"{prefix}%")
        ).order_by(desc(SupportTicket.ticket_number)).first()
        
        if last_ticket:
            last_seq = int(last_ticket.ticket_number.replace(prefix, ""))
            next_seq = last_seq + 1
        else:
            next_seq = 1
            
        return f"{prefix}{next_seq:05d}"


    # --- Feedback ---
    
    def get_feedback_list(self, skip: int = 0, limit: int = 50) -> Tuple[List[Feedback], int]:
        query = self.db.query(Feedback)
        total = query.count()
        feedback = query.order_by(desc(Feedback.created_at)).offset(skip).limit(limit).all()
        return feedback, total
        
    def create_feedback(self, data: dict) -> Feedback:
        feedback = Feedback(**data)
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback
        
    def delete_feedback(self, feedback: Feedback) -> None:
        self.db.delete(feedback)
        self.db.commit()


    # --- Statistics ---
    
    def get_statistics(self) -> Dict[str, Any]:
        total_articles = self.db.query(HelpArticle).count()
        total_categories = self.db.query(HelpCategory).count()
        
        total_tickets = self.db.query(SupportTicket).count()
        open_tickets = self.db.query(SupportTicket).filter(SupportTicket.status.in_(['Open', 'In Progress'])).count()
        resolved_tickets = self.db.query(SupportTicket).filter(SupportTicket.status.in_(['Resolved', 'Closed'])).count()
        
        total_feedback = self.db.query(Feedback).count()
        avg_rating = self.db.query(func.avg(Feedback.rating)).scalar() or 0.0
        
        return {
            "total_articles": total_articles,
            "total_categories": total_categories,
            "total_tickets": total_tickets,
            "open_tickets": open_tickets,
            "resolved_tickets": resolved_tickets,
            "total_feedback": total_feedback,
            "average_rating": float(avg_rating)
        }
