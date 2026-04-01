"""
Celery application setup for background workers.
"""
from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "polonium",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Explicitly import task modules so Celery can discover them.
celery_app.autodiscover_tasks(["app.workers.tasks"])

