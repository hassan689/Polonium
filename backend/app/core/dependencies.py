"""
This module defines shared FastAPI dependency aliases to keep route signatures
concise and consistent. It currently exposes a typed database session dependency.
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

DatabaseDep = Annotated[AsyncSession, Depends(get_db)]





