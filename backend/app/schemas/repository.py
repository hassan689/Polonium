"""
Repository-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl

from app.models.repository import RepositoryStatus


class RepositoryCreate(BaseModel):
    """Schema for creating a repository connection."""
    owner: str
    name: str


class RepositoryResponse(BaseModel):
    """Schema for repository response."""
    id: int
    github_owner: str
    github_name: str
    github_full_name: str
    github_url: str
    github_description: Optional[str]
    status: RepositoryStatus
    total_files: int
    total_size_bytes: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RepositoryOverviewResponse(BaseModel):
    """Schema for AI-generated repository overview."""
    overview: str
    architecture: Optional[str] = None
    tech_stack: Optional[list[str]] = None
    key_files: Optional[list[str]] = None
    generated_at: datetime

