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
        "app.tasks.research_tasks",
        "app.tasks.ai_topic_tasks",
        "app.tasks.usage_summary_tasks",
        "app.tasks.research_pipeline_tasks",
    ]
)

celery_app.conf.task_routes = {
    "tasks.enrich_frequency": {"queue": "frequency"},
    "tasks.enrich_definition": {"queue": "definition"},
    "tasks.run_basic_enrichment": {"queue": "control"},

    "tasks.research_word": {"queue": "search"},
    "tasks.classify_word_topics": {"queue": "ai"},
    "tasks.summarize_word_usage": {"queue": "ai"},
    "tasks.run_word_research_pipeline": {"queue": "control"},
    "tasks.run_research_pipeline": {"queue": "control"},
    "tasks.run_research_pipeline_until_done": {"queue": "control"},
}