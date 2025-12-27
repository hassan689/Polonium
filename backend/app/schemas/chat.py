"""
Chat-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.models.chat import MessageRole


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message."""
    content: str


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""
    id: int
    repository_id: int
    user_id: Optional[int]
    role: MessageRole
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

