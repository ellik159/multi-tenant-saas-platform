from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "saas_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Import tasks
from src.tasks import email_tasks, cleanup_tasks

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-old-audit-logs": {
        "task": "src.tasks.cleanup_tasks.cleanup_old_audit_logs",
        "schedule": 86400.0,  # Run daily
    },
}
