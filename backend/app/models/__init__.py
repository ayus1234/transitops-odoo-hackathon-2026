"""
SQLAlchemy models package.
"""
from app.core.database import Base
from app.models.role import Role
from app.models.user import User
from app.models.vehicle import Vehicle

__all__ = ["Base", "Role", "User", "Vehicle"]
