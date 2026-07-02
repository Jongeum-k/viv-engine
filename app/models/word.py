from sqlalchemy import BigInteger, DateTime, Integer, Numeric, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, List
from decimal import Decimal
from datetime import datetime

from app.models.base import Base


class Word(Base):
    __tablename__ = "words"

    __table_args__ = (
        UniqueConstraint("normalized_lemma", "part_of_speech"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    lemma: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_lemma: Mapped[str] = mapped_column(Text, nullable=False)
    part_of_speech: Mapped[Optional[str]] = mapped_column(Text)

    cefr_level: Mapped[Optional[str]] = mapped_column(Text)
    frequency_rank: Mapped[Optional[int]] = mapped_column(Integer)
    frequency_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))
    difficulty_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))

    source_count: Mapped[int] = mapped_column(Integer, server_default="0")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    sources: Mapped[List["WordSource"]] = relationship(
        "WordSource",
        back_populates="word",
        cascade="all, delete-orphan",
    )

    search_results: Mapped[List["WordSearchResult"]] = relationship(
        "WordSearchResult",
        back_populates="word",
        cascade="all, delete-orphan",
    )

    topic_scores: Mapped[List["WordTopicScore"]] = relationship(
        "WordTopicScore",
        back_populates="word",
        cascade="all, delete-orphan",
    )

    usage_summaries: Mapped[List["WordUsageSummary"]] = relationship(
        "WordUsageSummary",
        back_populates="word",
        cascade="all, delete-orphan",
    )

    definitions: Mapped[List["WordDefinition"]] = relationship(
        "WordDefinition",
        back_populates="word",
        cascade="all, delete-orphan",
    )