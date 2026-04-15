"""
Abstract embedding provider contract.
"""
from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddingProvider(ABC):
    """
    Contract for embedding providers.

    Design by contract:
    - Preconditions:
      - text inputs are non-empty after stripping whitespace
      - text inputs are reasonably bounded (target <= 512 tokens)
    - Postconditions:
      - each returned vector has consistent fixed dimension
      - batch output length equals input length
    """

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Embed a single text into a vector."""

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts into vectors."""

    @abstractmethod
    def get_dimension(self) -> int:
        """Return embedding dimension used by this provider."""

