from fastapi import APIRouter

from app.tasks.frequency_tasks import enrich_frequency
from app.tasks.definition_tasks import enrich_definition

router = APIRouter(prefix="/admin/jobs", tags=["admin-jobs"])


@router.post("/words/{word_id}/frequency")
def run_frequency_job(word_id: int):
    task = enrich_frequency.delay(word_id)

    return {
        "message": "Frequency job queued",
        "word_id": word_id,
        "task_id": task.id,
    }


@router.post("/words/{word_id}/definition")
def run_definition_job(word_id: int):
    task = enrich_definition.delay(word_id)

    return {
        "message": "Definition job queued",
        "word_id": word_id,
        "task_id": task.id,
    }


@router.post("/words/{word_id}/basic")
def run_basic_enrichment(word_id: int):
    frequency_task = enrich_frequency.delay(word_id)
    definition_task = enrich_definition.delay(word_id)

    return {
        "message": "Basic enrichment jobs queued",
        "word_id": word_id,
        "frequency_task_id": frequency_task.id,
        "definition_task_id": definition_task.id,
    }