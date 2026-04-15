"""
Application exception taxonomy.
"""


class PoloniumException(Exception):
    """Base application exception."""


class RepositoryError(PoloniumException):
    """Base repository-domain error."""


class RepositoryNotFoundError(RepositoryError):
    """Repository was not found."""


class RepositoryIndexingError(RepositoryError):
    """Repository indexing failed."""


class GitHubRateLimitError(RepositoryError):
    """GitHub API rate limit exceeded."""


class AIError(PoloniumException):
    """Base AI-domain error."""


class ModelLoadError(AIError):
    """Model failed to load."""


class InferenceTimeoutError(AIError):
    """Model inference timed out."""


class EmbeddingError(AIError):
    """Embedding generation failed."""


class DatabaseError(PoloniumException):
    """Database operation failed."""


class AuthenticationError(PoloniumException):
    """Authentication or authorization failure."""

