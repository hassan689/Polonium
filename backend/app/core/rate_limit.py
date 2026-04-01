"""
Redis-backed rate limiting decorator.
"""
from functools import wraps
from typing import Callable

from fastapi import HTTPException, Request
from redis import Redis

from app.core.config import settings


def _redis() -> Redis:
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)


def rate_limit(limit: int = 100, window: int = 60) -> Callable:
    """
    Limit requests per client+endpoint.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request | None = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if not request:
                return await func(*args, **kwargs)

            client_ip = request.client.host if request.client else "unknown"
            key = f"rl:{request.url.path}:{client_ip}"
            client = _redis()
            current = client.incr(key)
            if current == 1:
                client.expire(key, window)
            if current > limit:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            return await func(*args, **kwargs)

        return wrapper

    return decorator

