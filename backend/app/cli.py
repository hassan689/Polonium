"""
Polonium CLI entrypoint.
"""
import asyncio
import typer
import uvicorn
from sqlalchemy import text

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.workers.tasks.repository_tasks import ingest_repository_task

app = typer.Typer(help="Polonium developer CLI")


@app.command("health")
def health_check() -> None:
    """Run quick health checks for backend dependencies."""

    async def _run() -> None:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        typer.echo("OK: Database connection")
        typer.echo(f"OK: Redis URL configured -> {settings.REDIS_URL}")
        typer.echo(f"OK: Qdrant URL configured -> {settings.QDRANT_URL}")

    asyncio.run(_run())


@app.command("ingest")
def queue_repository_ingestion(repository_id: int) -> None:
    """Queue a repository ingestion job via Celery."""
    ingest_repository_task.delay(repository_id)
    typer.echo(f"Queued ingestion for repository_id={repository_id}")


@app.command("serve")
def serve(host: str = "0.0.0.0", port: int = 8000, reload: bool = True) -> None:
    """Run the FastAPI server."""
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()

