from celery import Celery

from app.config import settings

celery_app = Celery(
    "viv",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

celery_app.autodiscover_tasks(
    [
        "app.tasks.frequency_tasks",
        "app.tasks.definition_tasks",
        "app.tasks.basic_enrichment_tasks",
    ]
)

celery_app.conf.task_routes = {
    "tasks.enrich_frequency": {"queue": "frequency"},
    "tasks.enrich_definition": {"queue": "definition"},
    "tasks.run_basic_enrichment": {"queue": "control"},
}