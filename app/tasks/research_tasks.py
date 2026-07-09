from app.celery_app import celery_app
from app.config import settings
from app.db import SessionLocal
from app.models import Word, WordSearchResult

from app.tasks.pipeline_logging import add_pipeline_log

import httpx
from urllib.parse import urlparse


BRAVE_PROVIDER = "brave_search"


def get_domain(url: str) -> str:
    return urlparse(url).netloc.replace("www.", "")


@celery_app.task(name="tasks.research_word")
def research_word(word_id: int, pipeline_run_id: int) -> dict:
    db = SessionLocal()

    try:
        word = db.query(Word).filter(Word.id == word_id).first()

        if not word:
            return {"status": "skipped", "reason": "word not found", "word_id": word_id}

        existing_count = (
            db.query(WordSearchResult)
            .filter(
                WordSearchResult.word_id == word.id,
                WordSearchResult.provider_name == BRAVE_PROVIDER,
            )
            .count()
        )

        if existing_count >= 1:
            return {
                "status": "skipped",
                "reason": "search results already exist",
                "word_id": word.id,
                "pipeline_run_id": pipeline_run_id,
            }

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": settings.brave_search_api_key,
            "cache_control": "no-cache",
        }

        params = {
            "q": word.normalized_lemma,
            "count": 20,
        }

        response = httpx.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers=headers,
            params=params,
            timeout=20,
        )

        response.raise_for_status()
        payload = response.json()

        results = payload.get("web", {}).get("results", [])

        for index, item in enumerate(results, start=1):
            url = item.get("url")

            existing = (
                db.query(WordSearchResult)
                .filter(
                    WordSearchResult.word_id == word.id,
                    WordSearchResult.provider_name == BRAVE_PROVIDER,
                    WordSearchResult.result_rank == index,
                )
                .first()
            )

            if existing:
                existing.query_text = word.normalized_lemma
                existing.title = item.get("title")
                existing.snippet = item.get("description")
                existing.url = url
                existing.domain = get_domain(url) if url else None
                existing.raw_payload = item
            else:
                db.add(
                    WordSearchResult(
                        word_id=word.id,
                        provider_name=BRAVE_PROVIDER,
                        query_text=word.normalized_lemma,
                        result_rank=index,
                        title=item.get("title"),
                        snippet=item.get("description"),
                        url=url,
                        domain=get_domain(url) if url else None,
                        raw_payload=item,
                    )
                )

        add_pipeline_log(
            db,
            pipeline_run_id,
            "info",
            f"Research completed for {word.normalized_lemma}",
            {"word_id": word.id, "result_count": len(results)},
        )

        db.commit()

        return {
            "status": "success",
            "word_id": word.id,
            "pipeline_run_id": pipeline_run_id,
            "result_count": len(results),
        }

    finally:
        db.close()