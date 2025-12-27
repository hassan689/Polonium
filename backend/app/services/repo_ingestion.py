"""
Repository ingestion service for parsing and indexing repositories.
"""
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.repository import Repository, RepositoryStatus
from app.models.file import File
from app.services.github_service import GitHubService
from app.services.embedding_service import EmbeddingService
from app.services.ai_service import AIService
from app.core.config import settings


class RepoIngestionService:
    """Service for ingesting and indexing GitHub repositories."""
    
    def __init__(self):
        """Initialize ingestion service."""
        self.github_service = GitHubService()
        self.embedding_service = EmbeddingService()
        self.ai_service = AIService()
    
    async def ingest_repository(
        self,
        db: AsyncSession,
        repository_id: int,
        access_token: Optional[str] = None,
    ) -> Repository:
        """
        Ingest a repository: fetch files, generate embeddings, create overview.
        
        Args:
            db: Database session
            repository_id: Repository ID to ingest
            access_token: Optional GitHub access token
            
        Returns:
            Updated Repository object
        """
        # Fetch repository
        stmt = select(Repository).where(Repository.id == repository_id)
        result = await db.execute(stmt)
        repo = result.scalar_one_or_none()
        
        if not repo:
            raise ValueError(f"Repository {repository_id} not found")
        
        # Update status
        repo.status = RepositoryStatus.IN_PROGRESS
        repo.ingestion_started_at = datetime.utcnow()
        await db.commit()
        
        try:
            # Initialize GitHub service with token if provided
            github_service = GitHubService(access_token=access_token)
            
            # Fetch repository metadata
            repo_data = await github_service.get_repository(repo.github_owner, repo.github_name)
            repo.github_description = repo_data.get("description")
            repo.github_url = repo_data.get("html_url")
            
            # Fetch file tree
            files_tree = await github_service.get_repository_contents(
                repo.github_owner,
                repo.github_name,
                recursive=True,
            )
            
            # Filter and process files
            processed_files = []
            total_size = 0
            
            for file_entry in files_tree:
                file_path = file_entry.get("path", "")
                
                # Skip ignored files
                if github_service.should_ignore_file(file_path):
                    continue
                
                # Skip very large files (>1MB)
                if file_entry.get("size", 0) > 1_000_000:
                    continue
                
                try:
                    # Fetch file content
                    file_content = await github_service.get_file_content(
                        repo.github_owner,
                        repo.github_name,
                        file_path,
                    )
                    
                    # Create or update file record
                    file_hash = hashlib.sha256(file_content.encode()).hexdigest()
                    
                    # Check if file already exists
                    stmt = select(File).where(
                        File.repository_id == repository_id,
                        File.path == file_path,
                    )
                    result = await db.execute(stmt)
                    existing_file = result.scalar_one_or_none()
                    
                    if existing_file and existing_file.content_hash == file_hash:
                        # File unchanged, skip
                        processed_files.append(existing_file)
                        total_size += existing_file.size_bytes
                        continue
                    
                    # Create new file or update existing
                    file_path_obj = Path(file_path)
                    language = self._detect_language(file_path)
                    
                    file_data = {
                        "repository_id": repository_id,
                        "path": file_path,
                        "name": file_path_obj.name,
                        "extension": file_path_obj.suffix.lstrip(".") if file_path_obj.suffix else None,
                        "language": language,
                        "content": file_content,
                        "content_hash": file_hash,
                        "size_bytes": len(file_content.encode("utf-8")),
                        "line_count": len(file_content.splitlines()),
                    }
                    
                    if existing_file:
                        # Update existing
                        for key, value in file_data.items():
                            if key != "repository_id":
                                setattr(existing_file, key, value)
                        file_obj = existing_file
                    else:
                        # Create new
                        file_obj = File(**file_data)
                        db.add(file_obj)
                    
                    await db.flush()
                    
                    # Generate embedding
                    embedding_text = f"{file_path}\n{file_content[:5000]}"  # Limit for embedding
                    embedding = await self.embedding_service.generate_embedding(embedding_text)
                    
                    point_id = f"file_{file_obj.id}"
                    await self.embedding_service.store_embedding(
                        point_id=point_id,
                        vector=embedding,
                        payload={
                            "type": "file",
                            "repository_id": repository_id,
                            "file_id": file_obj.id,
                            "path": file_path,
                            "language": language,
                        },
                    )
                    
                    file_obj.qdrant_point_id = point_id
                    processed_files.append(file_obj)
                    total_size += file_obj.size_bytes
                    
                except Exception as e:
                    # Log error but continue with other files
                    print(f"Error processing file {file_path}: {e}")
                    continue
                
                # Commit periodically to avoid large transactions
                if len(processed_files) % 50 == 0:
                    await db.commit()
            
            # Update repository statistics
            repo.total_files = len(processed_files)
            repo.total_size_bytes = total_size
            
            # Generate repository overview
            file_summaries = [
                {
                    "path": f.path,
                    "summary": f"{f.language or 'unknown'} file, {f.line_count or 0} lines",
                }
                for f in processed_files[:100]  # Limit for overview
            ]
            
            overview_data = await self.ai_service.generate_repository_overview(
                repository_name=repo.github_full_name,
                file_summaries=file_summaries,
            )
            
            # Store overview as initial memory
            from app.services.memory_service import MemoryService
            memory_service = MemoryService()
            await memory_service.create_memory(
                db=db,
                repository_id=repository_id,
                title="Repository Overview",
                content=f"Overview: {overview_data['overview']}\n\nArchitecture: {overview_data.get('architecture', 'N/A')}",
                category="overview",
                metadata={
                    "tech_stack": overview_data.get("tech_stack", []),
                    "key_files": overview_data.get("key_files", []),
                },
            )
            
            # Mark as completed
            repo.status = RepositoryStatus.COMPLETED
            repo.ingestion_completed_at = datetime.utcnow()
            await db.commit()
            
            return repo
            
        except Exception as e:
            # Mark as failed
            repo.status = RepositoryStatus.FAILED
            repo.ingestion_error = str(e)
            await db.commit()
            raise
    
    def _detect_language(self, file_path: str) -> Optional[str]:
        """
        Detect programming language from file path/extension.
        
        Args:
            file_path: File path
            
        Returns:
            Detected language or None
        """
        extension_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "JavaScript",
            ".tsx": "TypeScript",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".cpp": "C++",
            ".c": "C",
            ".cs": "C#",
            ".php": "PHP",
            ".rb": "Ruby",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".scala": "Scala",
            ".html": "HTML",
            ".css": "CSS",
            ".sql": "SQL",
            ".sh": "Shell",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".json": "JSON",
            ".md": "Markdown",
            ".dockerfile": "Dockerfile",
            ".toml": "TOML",
            ".ini": "INI",
        }
        
        path_obj = Path(file_path)
        extension = path_obj.suffix.lower()
        
        return extension_map.get(extension)

