"""
Memory-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MemoryResponse(BaseModel):
    """Schema for repository memory response."""
    id: int
    repository_id: int
    title: str
    content: str
    category: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True





