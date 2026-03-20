"""
File-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FileResponse(BaseModel):
    """Schema for file response."""
    id: int
    repository_id: int
    path: str
    name: str
    extension: Optional[str]
    language: Optional[str]
    size_bytes: int
    line_count: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class FileExplanationResponse(BaseModel):
    """Schema for AI-generated file explanation."""
    file_path: str
    explanation: str
    purpose: Optional[str] = None
    key_functions: Optional[list[str]] = None
    dependencies: Optional[list[str]] = None
    generated_at: datetime





