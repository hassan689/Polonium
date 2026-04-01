"""
OpenAI-compatible embedding provider (fallback/dev).
"""
from typing import List
import requests

from app.core.config import settings
from app.services.embeddings.base import BaseEmbeddingProvider


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """Embedding provider via OpenAI-compatible /embeddings API."""

    def __init__(self):
        self.base_url = settings.LOCAL_LLM_BASE_URL.rstrip("/")
        self.api_key = settings.LOCAL_LLM_API_KEY
        self.model = settings.LOCAL_EMBEDDING_MODEL
        self._dimension = settings.EMBEDDING_VECTOR_SIZE

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _validate_text(self, text: str) -> None:
        if not text or not text.strip():
            raise ValueError("Embedding input text must be non-empty.")
        if len(text) > settings.EMBEDDING_MAX_CHARS:
            raise ValueError(
                f"Embedding input exceeds max chars ({settings.EMBEDDING_MAX_CHARS})."
            )

    def embed(self, text: str) -> List[float]:
        self._validate_text(text)
        response = requests.post(
            f"{self.base_url}/embeddings",
            headers=self._headers(),
            json={"model": self.model, "input": text},
            timeout=120,
        )
        response.raise_for_status()
        vector = response.json()["data"][0]["embedding"]
        if len(vector) != self._dimension:
            self._dimension = len(vector)
        return vector

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        for text in texts:
            self._validate_text(text)
        response = requests.post(
            f"{self.base_url}/embeddings",
            headers=self._headers(),
            json={"model": self.model, "input": texts},
            timeout=120,
        )
        response.raise_for_status()
        vectors = [item["embedding"] for item in response.json()["data"]]
        if vectors and len(vectors[0]) != self._dimension:
            self._dimension = len(vectors[0])
        return vectors

    def get_dimension(self) -> int:
        return self._dimension

