"""
This module boots the FastAPI application and composes cross-cutting platform
concerns: middleware, routing, structured error handling, health checks, and
Prometheus-compatible HTTP metrics for operational visibility.
"""
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from redis import Redis
from sqlalchemy import text
from qdrant_client import QdrantClient

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.exceptions import PoloniumException
from app.core.logging import setup_logging
from app.core.middleware import RequestContextMiddleware
from app.api.v1 import chat, files, repositories
from app.services.ai_service import AIService

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered collaborative workspace for GitHub repositories",
)

setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger("polonium.app")

REQUEST_COUNT = Counter("polonium_http_requests_total", "Total HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("polonium_http_request_duration_seconds", "HTTP request latency", ["method", "path"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestContextMiddleware)

app.include_router(repositories.router, prefix=settings.API_V1_PREFIX, tags=["repositories"])
app.include_router(chat.router, prefix=settings.API_V1_PREFIX, tags=["chat"])
app.include_router(files.router, prefix=settings.API_V1_PREFIX, tags=["files"])


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    path = request.url.path
    REQUEST_COUNT.labels(request.method, path, str(response.status_code)).inc()
    REQUEST_LATENCY.labels(request.method, path).observe(duration)
    return response


@app.exception_handler(PoloniumException)
async def polonium_exception_handler(request: Request, exc: PoloniumException):
    request_id = getattr(request.state, "request_id", None)
    logger.error(str(exc), extra={"request_id": request_id})
    return JSONResponse(
        status_code=400,
        content={"error": exc.__class__.__name__, "message": str(exc), "request_id": request_id},
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@app.get("/health/detailed")
async def health_detailed():
    """Detailed health checks for infrastructure dependencies."""
    checks = {
        "database": False,
        "redis": False,
        "qdrant": False,
        "ai_service": False,
    }

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        pass

    try:
        redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        checks["redis"] = bool(redis_client.ping())
    except Exception:
        pass

    try:
        qdrant = QdrantClient(url=settings.QDRANT_URL)
        qdrant.get_collections()
        checks["qdrant"] = True
    except Exception:
        pass

    try:
        ai_service = AIService()
        await ai_service.generate_chat_response(user_message="health check")
        checks["ai_service"] = True
    except Exception:
        pass

    healthy = all(checks.values())
    return {"status": "healthy" if healthy else "degraded", "checks": checks}


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return PlainTextResponse(data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)

