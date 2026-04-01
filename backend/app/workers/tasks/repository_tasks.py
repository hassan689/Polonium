"""
Background tasks for repository processing.
"""
import asyncio

from app.core.database import AsyncSessionLocal
from app.services.repo_ingestion import RepoIngestionService
from app.workers.celery_app import celery_app


@celery_app.task(name="repositories.ingest")
def ingest_repository_task(repository_id: int) -> dict:
    """
    Queue task: ingest and index a repository asynchronously.
    """
    async def _run() -> dict:
        async with AsyncSessionLocal() as db:
            service = RepoIngestionService()
            await service.ingest_repository(db=db, repository_id=repository_id)
            return {"repository_id": repository_id, "status": "completed"}

    return asyncio.run(_run())

