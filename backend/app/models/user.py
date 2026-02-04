"""User model"""
from sqlalchemy import Column, String, Boolean, Enum
from app.models.base import BaseModel
import enum


class UserRole(str, enum.Enum):
    """User roles"""

    ADMIN = "admin"
    SALES_MANAGER = "sales_manager"
    USER = "user"


class User(BaseModel):
    """User account"""

    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # SAML attributes
    saml_name_id = Column(String, unique=True, nullable=True)
    saml_session_index = Column(String, nullable=True)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
