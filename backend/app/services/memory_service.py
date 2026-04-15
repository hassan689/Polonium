"""
Memory service for managing repository-level AI memory.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import hashlib

from app.models.memory import RepositoryMemory
from app.services.embedding_service import EmbeddingService
from app.services.ai_service import AIService


class MemoryService:
    """Service for managing persistent repository memory."""
    
    def __init__(self):
        """Initialize memory service."""
        self.embedding_service = EmbeddingService()
        self.ai_service = AIService()
    
    async def get_relevant_memories(
        self,
        db: AsyncSession,
        repository_id: int,
        query: str,
        limit: int = 5,
    ) -> List[RepositoryMemory]:
        """
        Retrieve relevant memories for a query using semantic search.
        
        Args:
            db: Database session
            repository_id: Repository ID
            query: Query text
            limit: Maximum number of memories to return
            
        Returns:
            List of relevant RepositoryMemory objects
        """
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_embedding(query)
        
        # Search in Qdrant
        results = await self.embedding_service.search_similar(
            query_vector=query_embedding,
            limit=limit,
            filter_dict={
                "must": [
                    {"key": "type", "match": {"value": "memory"}},
                    {"key": "repository_id", "match": {"value": repository_id}},
                ]
            },
        )
        
        # Fetch full memory objects from database
        memory_ids = [int(r["payload"]["memory_id"]) for r in results]
        if not memory_ids:
            return []
        
        stmt = select(RepositoryMemory).where(
            RepositoryMemory.id.in_(memory_ids),
            RepositoryMemory.repository_id == repository_id,
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def create_memory(
        self,
        db: AsyncSession,
        repository_id: int,
        title: str,
        content: str,
        category: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> RepositoryMemory:
        """
        Create a new memory chunk.
        
        Args:
            db: Database session
            repository_id: Repository ID
            title: Memory title
            content: Memory content
            category: Optional category
            metadata: Optional metadata
            
        Returns:
            Created RepositoryMemory object
        """
        memory = RepositoryMemory(
            repository_id=repository_id,
            title=title,
            content=content,
            category=category,
            metadata=metadata or {},
        )
        db.add(memory)
        await db.flush()  # Get ID
        
        # Generate embedding and store in Qdrant
        embedding_text = f"{title}\n{content}"
        embedding = await self.embedding_service.generate_embedding(embedding_text)
        
        point_id = f"memory_{memory.id}"
        await self.embedding_service.store_embedding(
            point_id=point_id,
            vector=embedding,
            payload={
                "type": "memory",
                "repository_id": repository_id,
                "memory_id": memory.id,
                "title": title,
                "category": category,
            },
        )
        
        memory.qdrant_point_id = point_id
        await db.commit()
        await db.refresh(memory)
        
        return memory
    
    async def extract_memory_from_conversation(
        self,
        db: AsyncSession,
        repository_id: int,
        conversation_summary: str,
    ) -> Optional[RepositoryMemory]:
        """
        Extract and store important insights from a conversation.
        
        Args:
            db: Database session
            repository_id: Repository ID
            conversation_summary: Summary of conversation to extract insights from
            
        Returns:
            Created RepositoryMemory if insight was extracted, None otherwise
        """
        # Use AI to determine if there's a valuable insight
        prompt = f"""Review this conversation about a codebase:

{conversation_summary}

Determine if there's a valuable, reusable insight that should be remembered for future discussions. 
This could be:
- Architectural decisions
- Important patterns or conventions
- Key learnings about the codebase
- Common gotchas or important notes

If there's a valuable insight, format as JSON with keys: title, content, category.
If there's no valuable insight, return {{"extract": false}}."""

        result = await self.ai_service.generate_json_response(
            messages=[
                {
                    "role": "system",
                    "content": "You extract valuable, reusable insights from conversations. Return valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        
        if not result.get("extract", True):
            return None
        
        return await self.create_memory(
            db=db,
            repository_id=repository_id,
            title=result.get("title", "Insight"),
            content=result.get("content", ""),
            category=result.get("category"),
        )

