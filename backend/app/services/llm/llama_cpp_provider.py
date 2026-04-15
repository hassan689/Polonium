"""
llama-cpp-python LLM provider for GGUF models.
"""
from typing import Dict, List

from app.core.config import settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.exceptions import ConfigurationError, InferenceError, ModelLoadError


class LlamaCppProvider(BaseLLMProvider):
    def __init__(self):
        if not settings.LLAMA_CPP_MODEL_PATH:
            raise ConfigurationError("LLAMA_CPP_MODEL_PATH is required for llama_cpp provider.")
        try:
            from llama_cpp import Llama  # type: ignore

            self._model = Llama(
                model_path=settings.LLAMA_CPP_MODEL_PATH,
                n_ctx=settings.LLAMA_CPP_N_CTX,
                n_threads=settings.LLAMA_CPP_N_THREADS,
            )
        except Exception as exc:
            raise ModelLoadError(f"Failed to load llama.cpp model: {exc}") from exc

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        try:
            output = self._model.create_chat_completion(
                messages=messages,
                temperature=temperature,
            )
            return output["choices"][0]["message"]["content"]
        except Exception as exc:
            raise InferenceError(f"llama.cpp inference failed: {exc}") from exc

