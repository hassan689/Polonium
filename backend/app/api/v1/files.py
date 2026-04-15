"""
This module provides file exploration and file explanation endpoints for a
connected repository. It validates repository state, fetches file records, and
invokes AI-assisted explanation with repository memory context.
"""
from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.dependencies import DatabaseDep
from app.models.repository import Repository, RepositoryStatus
from app.models.file import File
from app.schemas.file import FileResponse, FileExplanationResponse
from app.services.ai_service import AIService
from app.services.memory_service import MemoryService

router = APIRouter()


@router.get("/repositories/{repository_id}/files", response_model=List[FileResponse])
async def list_files(
    repository_id: int,
    db: DatabaseDep,
    skip: int = 0,
    limit: int = 100,
    path_prefix: str = None,
):
    """List files in a repository."""
    stmt = select(Repository).where(Repository.id == repository_id)
    result = await db.execute(stmt)
    repository = result.scalar_one_or_none()
    
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    stmt = select(File).where(File.repository_id == repository_id)
    
    if path_prefix:
        stmt = stmt.where(File.path.startswith(path_prefix))
    
    stmt = stmt.order_by(File.path.asc()).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    files = result.scalars().all()
    
    return list(files)


@router.get("/repositories/{repository_id}/files/{file_path:path}", response_model=FileResponse)
async def get_file(
    repository_id: int,
    file_path: str,
    db: DatabaseDep,
):
    """Get file details."""
    stmt = select(Repository).where(Repository.id == repository_id)
    result = await db.execute(stmt)
    repository = result.scalar_one_or_none()
    
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    stmt = select(File).where(
        File.repository_id == repository_id,
        File.path == file_path,
    )
    result = await db.execute(stmt)
    file_obj = result.scalar_one_or_none()
    
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")
    
    return file_obj


@router.get("/repositories/{repository_id}/files/{file_path:path}/explain", response_model=FileExplanationResponse)
async def explain_file(
    repository_id: int,
    file_path: str,
    db: DatabaseDep,
):
    """Get AI-generated explanation for a file."""
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
    
    stmt = select(File).where(
        File.repository_id == repository_id,
        File.path == file_path,
    )
    result = await db.execute(stmt)
    file_obj = result.scalar_one_or_none()
    
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")
    
    if not file_obj.content:
        raise HTTPException(status_code=400, detail="File content not available")
    
    memory_service = MemoryService()
    memories = await memory_service.get_relevant_memories(
        db=db,
        repository_id=repository_id,
        query=f"explain {file_path}",
        limit=3,
    )
    memory_texts = [m.content for m in memories]
    repo_context = "\n".join(memory_texts) if memory_texts else None
    
    ai_service = AIService()
    explanation = await ai_service.explain_file(
        file_path=file_path,
        file_content=file_obj.content,
        repository_context=repo_context,
    )
    
    return explanation





