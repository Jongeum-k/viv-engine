from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import PipelineRun, PipelineLog

from app.tasks.frequency_tasks import enrich_frequency
from app.tasks.definition_tasks import enrich_definition
from app.tasks.basic_enrichment_tasks import run_basic_enrichment as run_basic_enrichment_task

router = APIRouter(prefix="/admin", tags=["admin-jobs"])


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


@router.post("/jobs/basic-enrichment")
def start_basic_enrichment(db: Session = Depends(get_db)):
    run = PipelineRun(
        job_name="basic_enrichment",
        status="created",
        source_name="admin_api",
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    task = run_basic_enrichment_task.delay(run.id)

    return {
        "message": "Basic enrichment queued",
        "pipeline_run_id": run.id,
        "task_id": task.id,
    }


@router.get("/pipeline/runs/{run_id}")
def get_pipeline_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(PipelineRun).filter(PipelineRun.id == run_id).first()

    if not run:
        return {"error": "Pipeline run not found"}

    return {
        "id": run.id,
        "job_name": run.job_name,
        "status": run.status,
        "total_records": run.total_records,
        "processed_records": run.processed_records,
        "inserted_records": run.inserted_records,
        "updated_records": run.updated_records,
        "failed_records": run.failed_records,
        "error_message": run.error_message,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
    }


@router.get("/pipeline/runs/{run_id}/logs")
def get_pipeline_logs(run_id: int, db: Session = Depends(get_db)):
    logs = (
        db.query(PipelineLog)
        .filter(PipelineLog.pipeline_run_id == run_id)
        .order_by(PipelineLog.created_at.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "id": log.id,
            "level": log.level,
            "message": log.message,
            "context": log.context,
            "created_at": log.created_at,
        }
        for log in logs
    ]