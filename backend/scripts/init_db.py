"""
Script to initialize the database and create initial migration.
Run this after setting up your database connection.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.database import Base
from app.core.config import settings
from app.models import *  # noqa: F401, F403


async def init_db():
    """Create all database tables."""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables created successfully!")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())

