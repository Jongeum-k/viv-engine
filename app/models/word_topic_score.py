from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class WordTopicScore(Base):
    __tablename__ = "word_topic_scores"

    __table_args__ = (
        UniqueConstraint("word_id", "topic_name", "provider_name"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    word_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("words.id", ondelete="CASCADE"),
        nullable=False,
    )

    topic_name: Mapped[str] = mapped_column(Text, nullable=False)
    provider_name: Mapped[str] = mapped_column(Text, nullable=False)

    score: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        server_default="0",
    )

    evidence_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    word: Mapped["Word"] = relationship(
        "Word",
        back_populates="topic_scores",
    )