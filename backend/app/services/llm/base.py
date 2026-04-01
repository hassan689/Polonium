"""
Abstract LLM provider contract.
"""
from abc import ABC, abstractmethod
from typing import Dict, List


class BaseLLMProvider(ABC):
    """Contract for pluggable LLM inference providers."""

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Generate a response for chat-style messages."""

