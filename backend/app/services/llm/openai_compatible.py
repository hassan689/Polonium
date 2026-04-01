"""
OpenAI-compatible LLM provider.
"""
from typing import Dict, List
import requests

from app.core.config import settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.exceptions import ConfigurationError, InferenceError


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(self):
        if not settings.LOCAL_LLM_BASE_URL:
            raise ConfigurationError("LOCAL_LLM_BASE_URL is required.")
        if not settings.LOCAL_LLM_MODEL:
            raise ConfigurationError("LOCAL_LLM_MODEL is required.")
        self.base_url = settings.LOCAL_LLM_BASE_URL.rstrip("/")
        self.model = settings.LOCAL_LLM_MODEL
        self.api_key = settings.LOCAL_LLM_API_KEY

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                },
                timeout=120,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as exc:
            raise InferenceError(f"OpenAI-compatible inference failed: {exc}") from exc

