from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class WordSearchResult(Base):
    __tablename__ = "word_search_results"

    __table_args__ = (
        UniqueConstraint("word_id", "provider_name", "result_rank"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    word_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("words.id", ondelete="CASCADE"),
        nullable=False,
    )

    provider_name: Mapped[str] = mapped_column(Text, nullable=False)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)

    result_rank: Mapped[int] = mapped_column(Integer, nullable=False)

    title: Mapped[Optional[str]] = mapped_column(Text)
    snippet: Mapped[Optional[str]] = mapped_column(Text)
    url: Mapped[Optional[str]] = mapped_column(Text)
    domain: Mapped[Optional[str]] = mapped_column(Text)

    raw_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    word: Mapped["Word"] = relationship(
        "Word",
        back_populates="search_results",
    )