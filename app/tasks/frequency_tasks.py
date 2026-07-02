from decimal import Decimal

from wordfreq import zipf_frequency

from app.celery_app import celery_app
from app.db import SessionLocal
from app.models import Word


CEFR_DIFFICULTY = {
    "A1": Decimal("1.0"),
    "A2": Decimal("2.0"),
    "B1": Decimal("3.0"),
    "B2": Decimal("4.0"),
    "C1": Decimal("5.0"),
    "C2": Decimal("6.0"),
}


def calculate_difficulty(zipf_score: float, cefr_level: str) -> Decimal:
    frequency_difficulty = Decimal(str(max(0, 8 - zipf_score)))
    cefr_difficulty = CEFR_DIFFICULTY.get(cefr_level, Decimal("3.0"))

    return (frequency_difficulty * Decimal("0.6")) + (cefr_difficulty * Decimal("0.4"))


@celery_app.task(name="tasks.enrich_frequency")
def enrich_frequency(word_id: int) -> dict:
    db = SessionLocal()

    try:
        word = db.query(Word).filter(Word.id == word_id).first()

        if not word:
            return {"status": "skipped", "reason": "word not found", "word_id": word_id}

        score = zipf_frequency(word.normalized_lemma, "en")

        word.frequency_score = Decimal(str(round(score, 4)))
        word.difficulty_score = calculate_difficulty(score, word.cefr_level)

        db.commit()

        return {
            "status": "success",
            "word_id": word_id,
            "word": word.normalized_lemma,
            "frequency_score": float(word.frequency_score),
            "difficulty_score": float(word.difficulty_score),
        }

    except Exception as exc:
        db.rollback()
        raise exc

    finally:
        db.close()