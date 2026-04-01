"""
Local sentence-transformers embedding provider.
"""
from typing import List

from app.core.config import settings
from app.services.embeddings.base import BaseEmbeddingProvider


class SentenceTransformerProvider(BaseEmbeddingProvider):
    """Embedding provider backed by sentence-transformers."""

    def __init__(self, model_name: str | None = None):
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except Exception as exc:
            raise RuntimeError(
                "sentence-transformers is required for EMBEDDING_PROVIDER=sentence_transformer"
            ) from exc

        self.model_name = model_name or settings.SENTENCE_TRANSFORMER_MODEL
        self._model = SentenceTransformer(self.model_name)
        self._dimension = int(self._model.get_sentence_embedding_dimension())

    def _validate_text(self, text: str) -> None:
        if not text or not text.strip():
            raise ValueError("Embedding input text must be non-empty.")
        if len(text) > settings.EMBEDDING_MAX_CHARS:
            raise ValueError(
                f"Embedding input exceeds max chars ({settings.EMBEDDING_MAX_CHARS})."
            )

    def embed(self, text: str) -> List[float]:
        self._validate_text(text)
        vector = self._model.encode(text, normalize_embeddings=settings.EMBEDDING_NORMALIZE)
        result = vector.tolist()
        if len(result) != self._dimension:
            raise RuntimeError("Provider returned inconsistent embedding dimension.")
        return result

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        for text in texts:
            self._validate_text(text)
        vectors = self._model.encode(texts, normalize_embeddings=settings.EMBEDDING_NORMALIZE)
        results = [vec.tolist() for vec in vectors]
        for vec in results:
            if len(vec) != self._dimension:
                raise RuntimeError("Provider returned inconsistent embedding dimension in batch.")
        return results

    def get_dimension(self) -> int:
        return self._dimension

