"""
Repository management API endpoints.
"""
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import DatabaseDep
from app.models.repository import Repository, RepositoryStatus
from app.schemas.repository import RepositoryCreate, RepositoryResponse, RepositoryOverviewResponse
from app.services.github_service import GitHubService
from app.services.repo_ingestion import RepoIngestionService
from app.services.ai_service import AIService
from app.services.memory_service import MemoryService

router = APIRouter()


@router.post("/repositories", response_model=RepositoryResponse, status_code=201)
async def create_repository(
    repo_data: RepositoryCreate,
    background_tasks: BackgroundTasks,
    db: DatabaseDep,
):
    """
    Connect a GitHub repository to Polonium.
    Starts ingestion in the background.
    """
    # Check if repository already exists
    full_name = f"{repo_data.owner}/{repo_data.name}"
    stmt = select(Repository).where(Repository.github_full_name == full_name)
    result = await db.execute(stmt)
    existing_repo = result.scalar_one_or_none()
    
    if existing_repo:
        raise HTTPException(
            status_code=400,
            detail=f"Repository {full_name} is already connected",
        )
    
    # Fetch repository metadata from GitHub
    github_service = GitHubService()
    try:
        repo_info = await github_service.get_repository(repo_data.owner, repo_data.name)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Repository not found or inaccessible: {str(e)}",
        )
    
    # Create repository record
    repository = Repository(
        github_owner=repo_data.owner,
        github_name=repo_data.name,
        github_full_name=full_name,
        github_url=repo_info.get("html_url", ""),
        github_description=repo_info.get("description"),
        status=RepositoryStatus.PENDING,
    )
    
    db.add(repository)
    await db.commit()
    await db.refresh(repository)
    
    # Start ingestion in background
    ingestion_service = RepoIngestionService()
    background_tasks.add_task(
        ingestion_service.ingest_repository,
        db=db,
        repository_id=repository.id,
    )
    
    return repository


@router.get("/repositories/{repository_id}", response_model=RepositoryResponse)
async def get_repository(
    repository_id: int,
    db: DatabaseDep,
):
    """Get repository details."""
    stmt = select(Repository).where(Repository.id == repository_id)
    result = await db.execute(stmt)
    repository = result.scalar_one_or_none()
    
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    return repository


@router.get("/repositories", response_model=List[RepositoryResponse])
async def list_repositories(
    db: DatabaseDep,
    skip: int = 0,
    limit: int = 100,
):
    """List all connected repositories."""
    stmt = select(Repository).offset(skip).limit(limit).order_by(Repository.created_at.desc())
    result = await db.execute(stmt)
    repositories = result.scalars().all()
    
    return list(repositories)


@router.get("/repositories/{repository_id}/overview", response_model=RepositoryOverviewResponse)
async def get_repository_overview(
    repository_id: int,
    db: DatabaseDep,
):
    """Get AI-generated repository overview."""
    # Fetch repository
    stmt = select(Repository).where(Repository.id == repository_id)
    result = await db.execute(stmt)
    repository = result.scalar_one_or_none()
    
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    if repository.status != RepositoryStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Repository ingestion not completed. Status: {repository.status}",
        )
    
    # Fetch existing memories
    memory_service = MemoryService()
    from app.models.memory import RepositoryMemory
    from sqlalchemy import select
    stmt = select(RepositoryMemory).where(RepositoryMemory.repository_id == repository_id)
    result = await db.execute(stmt)
    memories = result.scalars().all()
    memory_texts = [m.content for m in memories]
    
    # Fetch file summaries
    from app.models.file import File
    stmt = select(File).where(File.repository_id == repository_id).limit(100)
    result = await db.execute(stmt)
    files = result.scalars().all()
    
    file_summaries = [
        {
            "path": f.path,
            "summary": f"{f.language or 'unknown'} file, {f.line_count or 0} lines",
        }
        for f in files
    ]
    
    # Generate overview
    ai_service = AIService()
    overview_data = await ai_service.generate_repository_overview(
        repository_name=repository.github_full_name,
        file_summaries=file_summaries,
        existing_memories=memory_texts,
    )
    
    return overview_data

