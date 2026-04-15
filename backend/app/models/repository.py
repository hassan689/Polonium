"""
This module defines the repository persistence model and ingestion lifecycle
state used to track indexing progress, repository statistics, and relationships
to files, chat history, and long-term repository memory.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, JSON
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class RepositoryStatus(str, enum.Enum):
    """Repository ingestion status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Repository(Base):
    """GitHub repository model."""
    
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    github_owner = Column(String(255), nullable=False, index=True)
    github_name = Column(String(255), nullable=False, index=True)
    github_full_name = Column(String(512), nullable=False, unique=True, index=True)
    github_url = Column(String(1024), nullable=False)
    github_description = Column(Text, nullable=True)
    
    status = Column(Enum(RepositoryStatus), default=RepositoryStatus.PENDING, nullable=False)
    ingestion_started_at = Column(DateTime, nullable=True)
    ingestion_completed_at = Column(DateTime, nullable=True)
    ingestion_error = Column(Text, nullable=True)
    
    total_files = Column(Integer, default=0)
    total_size_bytes = Column(Integer, default=0)
    
    config = Column(JSON, default=dict)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    files = relationship("File", back_populates="repository", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="repository", cascade="all, delete-orphan")
    memories = relationship("RepositoryMemory", back_populates="repository", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Repository {self.github_full_name}>"





