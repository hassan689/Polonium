"""
This module defines chat message persistence for repository discussions,
including role attribution and optional AI context metadata.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MessageRole(str, enum.Enum):
    """Chat message role."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(Base):
    """Chat message in repository workspace."""
    
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    context = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    repository = relationship("Repository", back_populates="chat_messages")
    user = relationship("User", back_populates="chat_messages")
    
    def __repr__(self) -> str:
        return f"<ChatMessage {self.id} in repo {self.repository_id}>"





