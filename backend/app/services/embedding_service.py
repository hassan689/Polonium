"""
Embedding service for generating and managing vector embeddings.
"""
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from app.core.config import settings
from app.services.embeddings.factory import EmbeddingFactory
class EmbeddingService:
    """Service for generating embeddings and managing Qdrant vector store."""
    
    def __init__(self):
        """Initialize embedding service with local endpoint and Qdrant clients."""
        self.provider = EmbeddingFactory.create()
        self.qdrant_client = QdrantClient(url=settings.QDRANT_URL)
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure Qdrant collection exists with correct configuration."""
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if settings.QDRANT_COLLECTION_NAME not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=settings.QDRANT_COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=self.provider.get_dimension(),
                        distance=Distance.COSINE,
                    ),
                )
        except Exception as e:
            # Log error in production
            print(f"Error ensuring Qdrant collection: {e}")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using local embedding model.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        return self.provider.embed(text)
    
    async def store_embedding(
        self,
        point_id: str,
        vector: List[float],
        payload: dict,
    ) -> None:
        """
        Store embedding in Qdrant.
        
        Args:
            point_id: Unique identifier for the point
            vector: Embedding vector
            payload: Metadata payload
        """
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload=payload,
        )
        self.qdrant_client.upsert(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points=[point],
        )
    
    async def search_similar(
        self,
        query_vector: List[float],
        limit: int = 10,
        filter_dict: Optional[dict] = None,
    ) -> List[dict]:
        """
        Search for similar vectors in Qdrant.
        
        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            filter_dict: Optional filter dict with 'must' conditions
                        Example: {"must": [{"key": "type", "match": {"value": "file"}}]}
            
        Returns:
            List of similar points with scores
        """
        # Convert filter_dict to Qdrant Filter if provided
        query_filter = None
        if filter_dict:
            conditions = []
            for condition in filter_dict.get("must", []):
                if "key" in condition and "match" in condition:
                    conditions.append(
                        FieldCondition(
                            key=condition["key"],
                            match=MatchValue(value=condition["match"]["value"]),
                        )
                    )
            if conditions:
                query_filter = Filter(must=conditions)
        
        results = self.qdrant_client.search(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit,
            query_filter=query_filter,
        )
        
        return [
            {
                "id": result.id,
                "score": result.score,
                "payload": result.payload,
            }
            for result in results
        ]
    
    def delete_embedding(self, point_id: str) -> None:
        """
        Delete embedding from Qdrant.
        
        Args:
            point_id: Point ID to delete
        """
        self.qdrant_client.delete(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            points_selector=[point_id],
        )

