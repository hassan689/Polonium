"""
This module defines type-safe application configuration and environment profiles.
It centralizes runtime settings for infrastructure, AI providers, and security,
then resolves a concrete settings object by the selected environment.
"""
from pydantic_settings import BaseSettings
from typing import Optional, Type


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "Polonium"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/polonium"

    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION_NAME: str = "polonium_embeddings"
    
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_WEBHOOK_SECRET: Optional[str] = None
    
    LOCAL_LLM_BASE_URL: str = "http://localhost:11434/v1"
    LOCAL_LLM_API_KEY: Optional[str] = None
    LOCAL_LLM_MODEL: str = "llama3.1:8b"
    LOCAL_EMBEDDING_MODEL: str = "nomic-embed-text"
    EMBEDDING_VECTOR_SIZE: int = 768
    LLM_PROVIDER: str = "openai_compatible"
    LLAMA_CPP_MODEL_PATH: Optional[str] = None
    LLAMA_CPP_N_CTX: int = 4096
    LLAMA_CPP_N_THREADS: int = 4
    TRANSFORMERS_MODEL_ID: Optional[str] = None
    TRANSFORMERS_MAX_NEW_TOKENS: int = 512
    EMBEDDING_PROVIDER: str = "openai"
    SENTENCE_TRANSFORMER_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_MAX_CHARS: int = 4000
    EMBEDDING_NORMALIZE: bool = True
    FALLBACK_LLM_MODEL: Optional[str] = None
    AI_CACHE_TTL_SECONDS: int = 300
    
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


class DevelopmentSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    ENVIRONMENT: str = "development"


class TestSettings(Settings):
    DEBUG: bool = True
    LOG_LEVEL: str = "WARNING"
    ENVIRONMENT: str = "test"


class ProductionSettings(Settings):
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "production"


def get_settings() -> Settings:
    base = Settings()
    env = (base.ENVIRONMENT or "development").lower()
    mapping: dict[str, Type[Settings]] = {
        "development": DevelopmentSettings,
        "test": TestSettings,
        "production": ProductionSettings,
    }
    settings_cls = mapping.get(env, DevelopmentSettings)
    return settings_cls()


settings = get_settings()

