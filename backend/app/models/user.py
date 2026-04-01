"""
This module defines user persistence for authentication and identity mapping,
including GitHub profile fields and relationships to repository chat records.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """User model for GitHub OAuth authentication."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, nullable=False, index=True)
    github_username = Column(String(255), nullable=False, index=True)
    github_email = Column(String(255), nullable=True)
    github_avatar_url = Column(String(1024), nullable=True)
    
    github_access_token = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    chat_messages = relationship("ChatMessage", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User {self.github_username}>"





