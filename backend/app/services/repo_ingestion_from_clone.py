"""
Repository ingestion service that works with cloned repositories.
"""
import hashlib
from typing import Optional
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.repository import Repository, RepositoryStatus
from app.models.file import File
from app.services.embedding_service import EmbeddingService
from app.services.ai_service import AIService
from app.services.repo_clone_service import RepoCloneService
from app.core.config import settings


class RepoIngestionFromCloneService:
    """Service for ingesting repositories from cloned local storage."""
    
    def __init__(self):
        """Initialize ingestion service."""
        self.embedding_service = EmbeddingService()
        self.ai_service = AIService()
        self.clone_service = RepoCloneService()
    
    def should_ignore_file(self, file_path: Path) -> bool:
        """
        Check if a file should be ignored during ingestion.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file should be ignored
        """
        ignore_patterns = [
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            "env",
            ".env",
            "dist",
            "build",
            ".next",
            ".cache",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".DS_Store",
            "*.log",
            "*.tmp",
            ".idea",
            ".vscode",
        ]
        
        path_str = str(file_path)
        
        # Check if any ignore pattern matches
        for pattern in ignore_patterns:
            if pattern in path_str:
                return True
        
        return False
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
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
        
        extension = file_path.suffix.lower()
        return extension_map.get(extension)
    
    async def ingest_from_clone(
        self,
        db: AsyncSession,
        repository_id: int,
    ) -> Repository:
        """
        Ingest a repository from cloned local storage.
        
        Args:
            db: Database session
            repository_id: Repository ID to ingest
            
        Returns:
            Updated Repository object
        """
        # Fetch repository
        stmt = select(Repository).where(Repository.id == repository_id)
        result = await db.execute(stmt)
        repo = result.scalar_one_or_none()
        
        if not repo:
            raise ValueError(f"Repository {repository_id} not found")
        
        # Check if repository is cloned
        repo_path = self.clone_service.get_repository_path(repository_id)
        if not repo_path.exists():
            raise ValueError(f"Repository {repository_id} is not cloned. Please clone it first.")
        
        # Update status
        repo.status = RepositoryStatus.IN_PROGRESS
        repo.ingestion_started_at = datetime.utcnow()
        await db.commit()
        
        try:
            # Process files from cloned repository
            processed_files = []
            total_size = 0
            
            # Walk through repository directory
            for file_path in repo_path.rglob("*"):
                # Skip directories
                if file_path.is_dir():
                    continue
                
                # Skip ignored files
                if self.should_ignore_file(file_path):
                    continue
                
                # Get relative path from repo root
                try:
                    relative_path = file_path.relative_to(repo_path)
                except ValueError:
                    continue
                
                # Skip very large files (>1MB)
                if file_path.stat().st_size > 1_000_000:
                    continue
                
                try:
                    # Read file content
                    file_content = file_path.read_text(encoding="utf-8", errors="ignore")
                    
                    # Create or update file record
                    file_hash = hashlib.sha256(file_content.encode()).hexdigest()
                    
                    # Check if file already exists
                    stmt = select(File).where(
                        File.repository_id == repository_id,
                        File.path == str(relative_path),
                    )
                    result = await db.execute(stmt)
                    existing_file = result.scalar_one_or_none()
                    
                    if existing_file and existing_file.content_hash == file_hash:
                        # File unchanged, skip
                        processed_files.append(existing_file)
                        total_size += existing_file.size_bytes
                        continue
                    
                    # Create new file or update existing
                    language = self._detect_language(file_path)
                    
                    file_data = {
                        "repository_id": repository_id,
                        "path": str(relative_path),
                        "name": file_path.name,
                        "extension": file_path.suffix.lstrip(".") if file_path.suffix else None,
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
                    embedding_text = f"{relative_path}\n{file_content[:5000]}"  # Limit for embedding
                    embedding = await self.embedding_service.generate_embedding(embedding_text)
                    
                    point_id = f"file_{file_obj.id}"
                    await self.embedding_service.store_embedding(
                        point_id=point_id,
                        vector=embedding,
                        payload={
                            "type": "file",
                            "repository_id": repository_id,
                            "file_id": file_obj.id,
                            "path": str(relative_path),
                            "language": language,
                        },
                    )
                    
                    file_obj.qdrant_point_id = point_id
                    processed_files.append(file_obj)
                    total_size += file_obj.size_bytes
                    
                except Exception as e:
                    # Log error but continue with other files
                    print(f"Error processing file {relative_path}: {e}")
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

