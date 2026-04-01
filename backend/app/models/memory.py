"""
This module defines persistent repository memory records used to store reusable
AI context, including semantic-search references and structured metadata.
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
    
    title = Column(String(512), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    qdrant_point_id = Column(String(255), nullable=True, index=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    repository = relationship("Repository", back_populates="memories")
    
    def __repr__(self) -> str:
        return f"<RepositoryMemory {self.id} for repo {self.repository_id}>"

