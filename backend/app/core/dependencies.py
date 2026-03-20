"""
Shared dependencies for FastAPI routes.
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

# Type alias for database dependency
DatabaseDep = Annotated[AsyncSession, Depends(get_db)]





