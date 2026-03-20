"""
GitHub API integration service.
"""
import httpx
from typing import Optional, Dict, List, Any
from pathlib import Path

from app.core.config import settings


class GitHubService:
    """Service for interacting with GitHub API."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize GitHub service.
        
        Args:
            access_token: GitHub personal access token or OAuth token
        """
        self.access_token = access_token
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": f"{settings.APP_NAME}/{settings.APP_VERSION}",
        }
        if access_token:
            self.headers["Authorization"] = f"token {access_token}"
    
    async def get_repository(self, owner: str, name: str) -> Dict[str, Any]:
        """
        Fetch repository metadata from GitHub.
        
        Args:
            owner: Repository owner
            name: Repository name
            
        Returns:
            Repository metadata dictionary
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{name}",
                headers=self.headers,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
    
    async def get_repository_contents(
        self,
        owner: str,
        name: str,
        path: str = "",
        recursive: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Fetch repository file tree recursively.
        
        Args:
            owner: Repository owner
            name: Repository name
            path: Path to fetch (empty for root)
            recursive: Whether to fetch recursively (uses Git Trees API)
            
        Returns:
            List of file/directory entries
        """
        if recursive:
            # Use Git Trees API for recursive fetching
            async with httpx.AsyncClient() as client:
                # Get default branch
                repo_info = await self.get_repository(owner, name)
                default_branch = repo_info.get("default_branch", "main")
                
                # Get tree SHA
                branch_response = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{name}/branches/{default_branch}",
                    headers=self.headers,
                    timeout=30.0,
                )
                branch_response.raise_for_status()
                branch_data = branch_response.json()
                tree_sha = branch_data["commit"]["commit"]["tree"]["sha"]
                
                # Get recursive tree
                tree_response = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{name}/git/trees/{tree_sha}",
                    headers=self.headers,
                    params={"recursive": "1"},
                    timeout=60.0,  # Longer timeout for large repos
                )
                tree_response.raise_for_status()
                tree_data = tree_response.json()
                
                # Filter to only files (not directories)
                files = [
                    entry for entry in tree_data.get("tree", [])
                    if entry.get("type") == "blob"
                ]
                return files
        else:
            # Use Contents API (non-recursive)
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{name}/contents/{path}",
                    headers=self.headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
    
    async def get_file_content(
        self,
        owner: str,
        name: str,
        path: str,
    ) -> str:
        """
        Fetch file content from GitHub.
        
        Args:
            owner: Repository owner
            name: Repository name
            path: File path in repository
            
        Returns:
            File content as string
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{name}/contents/{path}",
                headers=self.headers,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            
            # Decode base64 content
            import base64
            content = base64.b64decode(data["content"]).decode("utf-8")
            return content
    
    def should_ignore_file(self, path: str) -> bool:
        """
        Check if file should be ignored during ingestion.
        
        Args:
            path: File path
            
        Returns:
            True if file should be ignored
        """
        # Common ignore patterns
        ignore_patterns = [
            ".git",
            "node_modules",
            "__pycache__",
            ".venv",
            "venv",
            "env",
            ".env",
            "dist",
            "build",
            ".next",
            ".pytest_cache",
            ".mypy_cache",
            ".DS_Store",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".coverage",
            "*.log",
            "*.tmp",
        ]
        
        path_lower = path.lower()
        path_parts = Path(path).parts
        
        for pattern in ignore_patterns:
            if pattern in path_parts or path_lower.endswith(pattern.lstrip("*")):
                return True
        
        return False





