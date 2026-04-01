"""
Simple Redis cache helpers.
"""
import json
from typing import Any, Optional

from redis import Redis

from app.core.config import settings


def get_redis_client() -> Redis:
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)


def cache_get_json(key: str) -> Optional[Any]:
    client = get_redis_client()
    value = client.get(key)
    if not value:
        return None
    return json.loads(value)


def cache_set_json(key: str, value: Any, ttl_seconds: int = 300) -> None:
    client = get_redis_client()
    client.setex(key, ttl_seconds, json.dumps(value))

