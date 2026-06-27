from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from app.models.base import Base


class WordSource(Base):
    __tablename__ = "word_sources"

    __table_args__ = (
        UniqueConstraint("word_id", "source_name"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    word_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("words.id", ondelete="CASCADE"),
        nullable=False,
    )

    source_name: Mapped[str] = mapped_column(Text, nullable=False)
    source_word: Mapped[Optional[str]] = mapped_column(Text)
    source_cefr_level: Mapped[Optional[str]] = mapped_column(Text)
    source_frequency_rank: Mapped[Optional[int]] = mapped_column(Integer)
    source_frequency_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4))

    raw_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    word: Mapped["Word"] = relationship(
        "Word",
        back_populates="sources",
    )