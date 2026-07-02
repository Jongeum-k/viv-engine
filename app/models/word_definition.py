from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class WordDefinition(Base):
    __tablename__ = "word_definitions"

    __table_args__ = (
        UniqueConstraint(
            "word_id",
            "provider_name",
            "language_code",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    word_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("words.id", ondelete="CASCADE"),
        nullable=False,
    )

    provider_name: Mapped[str] = mapped_column(Text, nullable=False)

    language_code: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="en",
    )

    phonetic: Mapped[Optional[str]] = mapped_column(Text)
    definition_summary: Mapped[Optional[str]] = mapped_column(Text)

    raw_payload: Mapped[Any] = mapped_column(JSONB, nullable=False)

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
        back_populates="definitions",
    )