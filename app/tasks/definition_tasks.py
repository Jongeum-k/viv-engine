from typing import Any, Dict, List, Optional

import httpx

from app.celery_app import celery_app
from app.db import SessionLocal
from app.models import Word, WordDefinition


DICTIONARY_PROVIDER = "dictionaryapi_dev"


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


def pick_definition_summary(payload: List[Dict[str, Any]]) -> Optional[str]:
    if not payload:
        return None

    for meaning in payload[0].get("meanings", []):
        for definition in meaning.get("definitions", []):
            text = definition.get("definition")
            if text:
                return text

    return None


@celery_app.task(name="tasks.enrich_definition")
def enrich_definition(word_id: int) -> dict:
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