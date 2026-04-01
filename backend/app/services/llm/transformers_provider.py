"""
HuggingFace transformers LLM provider.
"""
from typing import Dict, List

from app.core.config import settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.exceptions import ConfigurationError, InferenceError, ModelLoadError


class TransformersProvider(BaseLLMProvider):
    def __init__(self):
        if not settings.TRANSFORMERS_MODEL_ID:
            raise ConfigurationError("TRANSFORMERS_MODEL_ID is required for transformers provider.")
        try:
            from transformers import pipeline  # type: ignore

            self._pipeline = pipeline(
                "text-generation",
                model=settings.TRANSFORMERS_MODEL_ID,
            )
        except Exception as exc:
            raise ModelLoadError(f"Failed to load transformers model: {exc}") from exc

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        try:
            result = self._pipeline(
                prompt,
                max_new_tokens=settings.TRANSFORMERS_MAX_NEW_TOKENS,
                temperature=temperature,
                do_sample=True,
            )
            generated = result[0]["generated_text"]
            return generated[len(prompt) :].strip() if generated.startswith(prompt) else generated
        except Exception as exc:
            raise InferenceError(f"Transformers inference failed: {exc}") from exc

