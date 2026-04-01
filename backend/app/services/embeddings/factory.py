"""
Embedding provider factory.
"""
from app.core.config import settings
from app.services.embeddings.base import BaseEmbeddingProvider
from app.services.embeddings.openai_embedding import OpenAIEmbeddingProvider
from app.services.embeddings.sentence_transformer import SentenceTransformerProvider


class EmbeddingFactory:
    """Construct embedding provider based on configuration."""

    @staticmethod
    def create() -> BaseEmbeddingProvider:
        provider = settings.EMBEDDING_PROVIDER.lower()
        if provider == "sentence_transformer":
            return SentenceTransformerProvider()
        if provider == "openai":
            return OpenAIEmbeddingProvider()
        raise ValueError(
            f"Unsupported EMBEDDING_PROVIDER='{settings.EMBEDDING_PROVIDER}'. "
            "Expected one of: sentence_transformer, openai."
        )

