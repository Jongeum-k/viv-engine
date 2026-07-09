from collections import Counter
from decimal import Decimal
import json
import re

from app.config import settings

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.celery_app import celery_app
from app.db import SessionLocal
from app.models import Word, WordSearchResult, WordTopicScore

from app.tasks.pipeline_logging import add_pipeline_log


TOPICS = [
    "daily_life",
    "business_work",
    "technology",
    "medical_health",
    "legal_government",
    "education",
    "gaming_entertainment",
    "religion_philosophy",
    "unknown_other",
]


SYSTEM_PROMPT = """
You classify one search result for an English vocabulary word.

Choose exactly one topic:
- daily_life
- business_work
- technology
- medical_health
- legal_government
- education
- gaming_entertainment
- religion_philosophy
- unknown_other

Rules:
- Use only the given evidence.
- Classify the context where the word appears, not the dictionary meaning.
- If evidence is weak or unclear, choose unknown_other.
- Return valid JSON only.
"""

USER_PROMPT = """
Word: {word}

Evidence:
Title: {title}
Snippet: {snippet}
Domain: {domain}

Return exactly:
{{
  "topic": "one_topic_from_the_list",
  "confidence": "low|medium|high",
  "reason": "short sentence"
}}
"""

def get_chain():
    llm = ChatOpenAI(
        model="gpt-5.4-nano",
        temperature=0,
        api_key=settings.openai_api_key,
    )
    return prompt | llm

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("user", USER_PROMPT),
    ]
)

chain = get_chain()

def parse_json(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            return {"topic": "unknown_other", "confidence": "low", "reason": "No JSON returned"}
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {"topic": "unknown_other", "confidence": "low", "reason": "Invalid JSON returned"}


@celery_app.task(name="tasks.classify_word_topics")
def classify_word_topics(previous_result: dict) -> dict:
    word_id = previous_result["word_id"]

    db = SessionLocal()

    try:
        word = db.query(Word).filter(Word.id == word_id).first()

        existing_count = (
            db.query(WordTopicScore)
            .filter(
                WordTopicScore.word_id == word_id,
                WordTopicScore.provider_name == "openai_topic_classifier",
            )
            .count()
        )

        if existing_count > 0:
            return {
                **previous_result,
                "status": "skipped",
                "reason": "topic scores already exist",
            }

        results = (
            db.query(WordSearchResult)
            .filter(WordSearchResult.word_id == word_id)
            .order_by(WordSearchResult.result_rank.asc())
            .all()
        )

        votes = Counter()
        classifications = []

        for result in results:
            response = chain.invoke(
                {
                    "word": word.normalized_lemma,
                    "title": result.title or "",
                    "snippet": result.snippet or "",
                    "domain": result.domain or "",
                }
            )

            data = parse_json(response.content)
            topic = data.get("topic")

            if topic not in TOPICS:
                topic = "unknown_other"

            votes[topic] += 1

            classifications.append(
                {
                    "search_result_id": result.id,
                    "rank": result.result_rank,
                    "topic": topic,
                    "confidence": data.get("confidence", "low"),
                    "reason": data.get("reason", ""),
                }
            )

        for topic, score in votes.items():
            existing = (
                db.query(WordTopicScore)
                .filter(
                    WordTopicScore.word_id == word_id,
                    WordTopicScore.topic_name == topic,
                    WordTopicScore.provider_name == "openai_topic_classifier",
                )
                .first()
            )

            if existing:
                existing.score = Decimal(str(score))
                existing.evidence_count = score
            else:
                db.add(
                    WordTopicScore(
                        word_id=word_id,
                        topic_name=topic,
                        provider_name="openai_topic_classifier",
                        score=Decimal(str(score)),
                        evidence_count=score,
                    )
                )

        add_pipeline_log(
            db,
            previous_result["pipeline_run_id"],
            "info",
            f"Topic classification completed for {word.normalized_lemma}",
            {"word_id": word.id, "topic_votes": dict(votes)},
        )

        db.commit()

        return {
            "status": "success",
            "word_id": word_id,
            "topic_votes": dict(votes),
            "classifications": classifications,
            "pipeline_run_id": previous_result["pipeline_run_id"],
        }

    finally:
        db.close()