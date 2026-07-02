from app.celery_app import celery_app
from app.db import SessionLocal
from app.models import Word, PipelineRun, PipelineLog
from app.tasks.frequency_tasks import enrich_frequency
from app.tasks.definition_tasks import enrich_definition


ENRICHMENT_LEVELS = {"B1", "B2", "C1", "C2"}


@celery_app.task(name="tasks.run_basic_enrichment")
def run_basic_enrichment(pipeline_run_id: int) -> dict:
    db = SessionLocal()

    try:
        run = db.query(PipelineRun).filter(PipelineRun.id == pipeline_run_id).first()
        run.status = "running"
        db.commit()

        words = (
            db.query(Word)
            .filter(Word.cefr_level.in_(ENRICHMENT_LEVELS))
            .all()
        )

        run.total_records = len(words)
        db.commit()

        for word in words:
            enrich_frequency.delay(word.id)
            enrich_definition.delay(word.id)

            run.processed_records += 1

            db.add(
                PipelineLog(
                    pipeline_run_id=run.id,
                    level="info",
                    message=f"Queued basic enrichment for {word.normalized_lemma}",
                    context={"word_id": word.id},
                )
            )

            db.commit()

        run.status = "queued"
        db.commit()

        return {
            "status": "queued",
            "pipeline_run_id": pipeline_run_id,
            "queued_words": len(words),
        }

    except Exception as exc:
        db.rollback()

        if "run" in locals() and run:
            run.status = "failed"
            run.error_message = str(exc)
            db.commit()

        raise exc

    finally:
        db.close()