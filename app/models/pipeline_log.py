from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PipelineLog(Base):
    __tablename__ = "pipeline_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    pipeline_run_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("pipeline_runs.id", ondelete="CASCADE"),
    )

    level: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="info",
    )

    message: Mapped[str] = mapped_column(Text, nullable=False)

    context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    pipeline_run: Mapped[Optional["PipelineRun"]] = relationship(
        "PipelineRun",
        back_populates="logs",
    )