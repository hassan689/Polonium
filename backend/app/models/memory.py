"""
Repository memory model for persistent AI context.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class RepositoryMemory(Base):
    """Persistent memory chunks for repository-level AI context."""
    
    __tablename__ = "repository_memories"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Memory content
    title = Column(String(512), nullable=False)  # Brief title/description
    content = Column(Text, nullable=False)  # Memory content
    category = Column(String(100), nullable=True)  # e.g., "architecture", "pattern", "decision"
    
    # Embedding reference for semantic search
    qdrant_point_id = Column(String(255), nullable=True, index=True)
    
    # Metadata
    metadata = Column(JSON, default=dict)  # Additional context (files, timestamps, etc.)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    repository = relationship("Repository", back_populates="memories")
    
    def __repr__(self) -> str:
        return f"<RepositoryMemory {self.id} for repo {self.repository_id}>"

