from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.config import settings

from app.celery_app import celery_app
from app.db import SessionLocal
from app.models import Word, WordTopicScore, WordUsageSummary

from app.tasks.pipeline_logging import add_pipeline_log


SUMMARY_SYSTEM_PROMPT = """
You summarize how web users appear to use an English word.

Rules:
- Use only the provided topic scores and reasons.
- Focus on real-world usage, not dictionary meaning.
- Keep it to 1 or 2 short sentences.
- Do not use bullet points.
"""

SUMMARY_USER_PROMPT = """
Word: {word}

Topic scores and evidence:
{evidence}

Write a short usage summary.
"""


llm = ChatOpenAI(model="gpt-5.4-nano", temperature=0, api_key=settings.openai_api_key)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SUMMARY_SYSTEM_PROMPT),
        ("user", SUMMARY_USER_PROMPT),
    ]
)

summary_chain = prompt | llm


@celery_app.task(name="tasks.summarize_word_usage")
def summarize_word_usage(previous_result: dict) -> dict:
    word_id = previous_result["word_id"]

    db = SessionLocal()

    try:
        word = db.query(Word).filter(Word.id == word_id).first()

        existing = (
            db.query(WordUsageSummary)
            .filter(
                WordUsageSummary.word_id == word_id,
                WordUsageSummary.provider_name == "openai",
                WordUsageSummary.model_name == "gpt-5.4-nano",
                WordUsageSummary.prompt_version == "usage-summary-v1",
            )
            .first()
        )

        if existing:
            return {
                "status": "skipped",
                "reason": "usage summary already exists",
                "word_id": word_id,
                "pipeline_run_id": previous_result["pipeline_run_id"],
            }

        topic_scores = (
            db.query(WordTopicScore)
            .filter(WordTopicScore.word_id == word_id)
            .all()
        )

        evidence = {
            "topic_scores": [
                {
                    "topic": item.topic_name,
                    "score": str(item.score),
                    "evidence_count": item.evidence_count,
                }
                for item in topic_scores
            ],
            "classifications": previous_result.get("classifications", []),
        }

        response = summary_chain.invoke(
            {
                "word": word.normalized_lemma,
                "evidence": evidence,
            }
        )

        summary = response.content.strip()

        existing = (
            db.query(WordUsageSummary)
            .filter(
                WordUsageSummary.word_id == word_id,
                WordUsageSummary.provider_name == "openai",
                WordUsageSummary.model_name == "gpt-5.4-nano",
                WordUsageSummary.prompt_version == "usage-summary-v1",
            )
            .first()
        )

        if existing:
            existing.summary = summary
            existing.raw_payload = previous_result
        else:
            db.add(
                WordUsageSummary(
                    word_id=word_id,
                    provider_name="openai",
                    model_name="gpt-5.4-nano",
                    prompt_version="usage-summary-v1",
                    summary=summary,
                    raw_payload=previous_result,
                )
            )

        add_pipeline_log(
            db,
            previous_result["pipeline_run_id"],
            "info",
            f"Usage summary completed for {word.normalized_lemma}",
            {"word_id": word.id},
        )

        db.commit()

        return {
            "status": "success",
            "word_id": word_id,
            "summary": summary,
            "pipeline_run_id": previous_result["pipeline_run_id"],
        }

    finally:
        db.close()