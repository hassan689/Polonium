"""
LLM provider factory.
"""
from app.core.config import settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.exceptions import ConfigurationError
from app.services.llm.llama_cpp_provider import LlamaCppProvider
from app.services.llm.openai_compatible import OpenAICompatibleProvider
from app.services.llm.transformers_provider import TransformersProvider


class LLMFactory:
    """Construct LLM provider based on LLM_PROVIDER."""

    @staticmethod
    def create() -> BaseLLMProvider:
        provider = settings.LLM_PROVIDER.lower()
        if provider == "openai_compatible":
            return OpenAICompatibleProvider()
        if provider == "llama_cpp":
            return LlamaCppProvider()
        if provider == "transformers":
            return TransformersProvider()
        raise ConfigurationError(
            f"Unsupported LLM_PROVIDER='{settings.LLM_PROVIDER}'. "
            "Expected one of: openai_compatible, llama_cpp, transformers."
        )

