"""
File model for repository files.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from app.core.database import Base


class File(Base):
    """Repository file model with embedding reference."""
    
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # File metadata
    path = Column(String(2048), nullable=False, index=True)
    name = Column(String(512), nullable=False)
    extension = Column(String(50), nullable=True)
    language = Column(String(100), nullable=True)  # Detected programming language
    
    # Content
    content = Column(Text, nullable=True)  # Store file content (can be large)
    content_hash = Column(String(64), nullable=True, index=True)  # SHA-256 hash
    
    # Size and metadata
    size_bytes = Column(Integer, nullable=False, default=0)
    line_count = Column(Integer, nullable=True)
    
    # Embedding reference
    qdrant_point_id = Column(String(255), nullable=True, index=True)  # Qdrant vector ID
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    repository = relationship("Repository", back_populates="files")
    
    def __repr__(self) -> str:
        return f"<File {self.path} in repo {self.repository_id}>"





