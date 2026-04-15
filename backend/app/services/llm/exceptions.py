"""Custom exceptions for LLM providers."""


class ConfigurationError(Exception):
    """Raised when provider settings are missing or invalid."""


class ModelLoadError(Exception):
    """Raised when model initialization/loading fails."""


class InferenceError(Exception):
    """Raised when model inference/generation fails."""

