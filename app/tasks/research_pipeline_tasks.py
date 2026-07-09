from celery import chain
from sqlalchemy import exists, and_

from app.celery_app import celery_app
from app.db import SessionLocal
from app.models import Word
from app.models import WordSearchResult, WordTopicScore, WordUsageSummary, PipelineRun

from app.tasks.research_tasks import research_word
from app.tasks.ai_topic_tasks import classify_word_topics
from app.tasks.usage_summary_tasks import summarize_word_usage


WEB_AI_LEVELS = {"B2", "C1", "C2"}


@celery_app.task(name="tasks.run_word_research_pipeline")
def run_word_research_pipeline(word_id: int, pipeline_run_id: int) -> dict:
    chain(
        research_word.s(word_id, pipeline_run_id),
        classify_word_topics.s(),
        summarize_word_usage.s(),
    ).delay()

    return {
        "status": "queued",
        "word_id": word_id,
        "pipeline_run_id": pipeline_run_id,
    }


@celery_app.task(name="tasks.run_research_pipeline")
def run_research_pipeline(pipeline_run_id: int, limit: int = 100) -> dict:
    db = SessionLocal()

    try:
        words = (
            db.query(Word)
            .filter(Word.cefr_level.in_(WEB_AI_LEVELS))
            .filter(
                ~exists().where(
                    and_(
                        WordUsageSummary.word_id == Word.id,
                        WordUsageSummary.provider_name == "openai",
                        WordUsageSummary.model_name == "gpt-5.4-nano",
                        WordUsageSummary.prompt_version == "usage-summary-v1",
                    )
                )
            )
            .limit(limit)
            .all()
        )

        for word in words:
            run_word_research_pipeline.delay(word.id, pipeline_run_id)

        return {
            "status": "queued",
            "queued_words": len(words),
        }

    finally:
        db.close()

@celery_app.task(name="tasks.run_research_pipeline_until_done")
def run_research_pipeline_until_done(pipeline_run_id: int, batch_size: int = 100) -> dict:
    db = SessionLocal()

    try:
        run = db.query(PipelineRun).filter(PipelineRun.id == pipeline_run_id).first()
        run.status = "running"
        db.commit()

        words = (
            db.query(Word)
            .filter(Word.cefr_level.in_(WEB_AI_LEVELS))
            .filter(
                ~exists().where(
                    and_(
                        WordUsageSummary.word_id == Word.id,
                        WordUsageSummary.provider_name == "openai",
                        WordUsageSummary.model_name == "gpt-5.4-nano",
                        WordUsageSummary.prompt_version == "usage-summary-v1",
                    )
                )
            )
            .limit(batch_size)
            .all()
        )

        if not words:
            run.status = "completed"
            db.commit()
            return {
                "status": "completed",
                "pipeline_run_id": pipeline_run_id,
                "queued_words": 0,
            }

        for word in words:
            run_word_research_pipeline.delay(word.id, pipeline_run_id)

        run.total_records += len(words)
        run.status = "running"
        db.commit()

        # Queue the next controller check after a delay.
        # This gives child workers time to finish some summaries.
        run_research_pipeline_until_done.apply_async(
            args=[pipeline_run_id, batch_size],
            countdown=300,
        )

        return {
            "status": "batch_queued",
            "pipeline_run_id": pipeline_run_id,
            "queued_words": len(words),
            "next_batch_check_seconds": 300,
        }

    except Exception as exc:
        db.rollback()

        if "run" in locals() and run:
            run.status = "failed"
            run.error_message = str(exc)
            db.commit()

        raise

    finally:
        db.close()