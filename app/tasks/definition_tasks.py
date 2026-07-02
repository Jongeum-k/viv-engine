from typing import Any, Dict, List, Optional

import httpx

from app.celery_app import celery_app
from app.db import SessionLocal
from app.models import Word, WordDefinition


DICTIONARY_PROVIDER = "dictionaryapi_dev"
DICTIONARY_RATE_LIMIT = "1/s"
DICTIONARY_MAX_RETRIES = 5
DICTIONARY_MAX_RETRIES_SECONDS = 30

def pick_phonetic(payload: List[Dict[str, Any]]) -> Optional[str]:
    if not payload:
        return None

    entry = payload[0]

    if entry.get("phonetic"):
        return entry["phonetic"]

    for item in entry.get("phonetics", []):
        if item.get("text"):
            return item["text"]

    return None

def get_retry_countdown(response: httpx.Response, retry_number: int) -> int:
    retry_after = response.headers.get("Retry-After")

    if retry_after and retry_after.idigit():
        return int(retry_after)

    return min(
        DICTIONARY_MAX_RETRIES_SECONDS * (retry_number + 1),
        300,
    )


def pick_definition_summary(payload: List[Dict[str, Any]]) -> Optional[str]:
    if not payload:
        return None

    for meaning in payload[0].get("meanings", []):
        for definition in meaning.get("definitions", []):
            text = definition.get("definition")
            if text:
                return text

    return None


@celery_app.task(
    name="tasks.enrich_definition",
    bind=True,
    max_retries=DICTIONARY_MAX_RETRIES,
    rate_limit=DICTIONARY_RATE_LIMIT,
)
def enrich_definition(self, word_id: int) -> dict:
    db = SessionLocal()

    try:
        word = db.query(Word).filter(Word.id == word_id).first()

        if not word:
            return {"status": "skipped", "reason": "word not found", "word_id": word_id}

        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.normalized_lemma}"

        response = httpx.get(url, timeout=10)

        if response.status_code == 404:
            return {
                "status": "skipped",
                "reason": "definition not found",
                "word_id": word_id,
                "word": word.normalized_lemma,
            }

        if response.status_code == 429:
            countdown = get_retry_countdown(
                response=response,
                retry_number=self.request.retries,
            )

            raise self.retry(
                countdown=countdown,
                exc=httpx.HTTPStatusError(
                    "Dictionary API rate limit exceeded",
                    request=response.request,
                    response=response,
                ),
            )

        if response.status_code >= 500:
            countdown = get_retry_countdown(
                response=response,
                retry_number=self.request.retries,
            )

            raise self.retry(
                countdown=countdown,
                exc=httpx.HTTPStatusError(
                    "Dictionary API temporary server error",
                    request=response.request,
                    response=response,
                ),
            )

        response.raise_for_status()
        payload = response.json()

        existing = (
            db.query(WordDefinition)
            .filter(
                WordDefinition.word_id == word.id,
                WordDefinition.provider_name == DICTIONARY_PROVIDER,
                WordDefinition.language_code == "en",
            )
            .first()
        )

        if existing:
            existing.phonetic = pick_phonetic(payload)
            existing.definition_summary = pick_definition_summary(payload)
            existing.raw_payload = payload
        else:
            definition = WordDefinition(
                word_id=word.id,
                provider_name=DICTIONARY_PROVIDER,
                language_code="en",
                phonetic=pick_phonetic(payload),
                definition_summary=pick_definition_summary(payload),
                raw_payload=payload,
            )
            db.add(definition)

        db.commit()

        return {
            "status": "success",
            "word_id": word_id,
            "word": word.normalized_lemma,
        }

    except Exception as exc:
        db.rollback()
        raise exc

    finally:
        db.close()