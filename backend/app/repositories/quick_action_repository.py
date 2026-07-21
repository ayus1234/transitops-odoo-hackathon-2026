"""
Quick Actions repository layer for database operations.
"""
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import func, or_, desc
from sqlalchemy.orm import Session, joinedload

from app.models.quick_action import QuickAction, UserFavoriteAction, UserRecentAction


class QuickActionRepository:
    """Repository for managing quick actions in the database."""
    
    def __init__(self, db: Session):
        self.db = db
        
    def get_action(self, action_id: UUID) -> Optional[QuickAction]:
        return self.db.query(QuickAction).filter(QuickAction.id == action_id).first()
        
    def list_active_actions(self) -> List[QuickAction]:
        return self.db.query(QuickAction).filter(QuickAction.is_active == True)\
            .order_by(QuickAction.display_order.asc(), QuickAction.display_name.asc()).all()
            
    def search_actions(self, keyword: Optional[str] = None, category: Optional[str] = None) -> List[QuickAction]:
        query = self.db.query(QuickAction).filter(QuickAction.is_active == True)
        
        if category:
            query = query.filter(func.lower(QuickAction.category) == category.lower())
            
        if keyword:
            search_term = f"%{keyword}%"
            query = query.filter(
                or_(
                    QuickAction.name.ilike(search_term),
                    QuickAction.display_name.ilike(search_term),
                    QuickAction.description.ilike(search_term)
                )
            )
            
        return query.order_by(QuickAction.display_order.asc(), QuickAction.display_name.asc()).all()
        
    def get_user_favorites(self, user_id: UUID) -> List[UUID]:
        favorites = self.db.query(UserFavoriteAction.action_id)\
            .filter(UserFavoriteAction.user_id == user_id).all()
        return [f[0] for f in favorites]
        
    def get_user_recent_actions(self, user_id: UUID, limit: int = 10) -> List[UserRecentAction]:
        return self.db.query(UserRecentAction)\
            .options(joinedload(UserRecentAction.action))\
            .filter(UserRecentAction.user_id == user_id)\
            .join(QuickAction)\
            .filter(QuickAction.is_active == True)\
            .order_by(desc(UserRecentAction.last_accessed_at))\
            .limit(limit).all()
            
    def toggle_favorite(self, user_id: UUID, action_id: UUID, is_favorite: bool) -> bool:
        """Toggles a favorite. Returns the new favorite status."""
        existing = self.db.query(UserFavoriteAction).filter(
            UserFavoriteAction.user_id == user_id,
            UserFavoriteAction.action_id == action_id
        ).first()
        
        if is_favorite and not existing:
            new_fav = UserFavoriteAction(user_id=user_id, action_id=action_id)
            self.db.add(new_fav)
            self.db.commit()
            return True
        elif not is_favorite and existing:
            self.db.delete(existing)
            self.db.commit()
            return False
            
        return existing is not None
        
    def log_execution(self, user_id: UUID, action_id: UUID) -> None:
        """Log the execution of an action for a user."""
        recent = self.db.query(UserRecentAction).filter(
            UserRecentAction.user_id == user_id,
            UserRecentAction.action_id == action_id
        ).first()
        
        if recent:
            recent.access_count += 1
            recent.last_accessed_at = datetime.utcnow()
        else:
            recent = UserRecentAction(user_id=user_id, action_id=action_id)
            self.db.add(recent)
            
        self.db.commit()
        
    def get_statistics(self, user_id: UUID) -> Dict[str, Any]:
        total = self.db.query(QuickAction).count()
        active = self.db.query(QuickAction).filter(QuickAction.is_active == True).count()
        favorites = self.db.query(UserFavoriteAction).filter(UserFavoriteAction.user_id == user_id).count()
        recent = self.db.query(UserRecentAction).filter(UserRecentAction.user_id == user_id).count()
        
        return {
            "total_actions": total,
            "active_actions": active,
            "favorites_count": favorites,
            "recent_actions_count": recent
        }
