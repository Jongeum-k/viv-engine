from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class WordUsageSummary(Base):
    __tablename__ = "word_usage_summaries"

    __table_args__ = (
        UniqueConstraint(
            "word_id",
            "provider_name",
            "model_name",
            "prompt_version",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    word_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("words.id", ondelete="CASCADE"),
        nullable=False,
    )

    provider_name: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_version: Mapped[str] = mapped_column(Text, nullable=False)

    summary: Mapped[str] = mapped_column(Text, nullable=False)
    raw_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

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
        back_populates="usage_summaries",
    )