from sqlalchemy import BigInteger, DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime

from app.models.base import Base


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    job_name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    source_name: Mapped[Optional[str]] = mapped_column(Text)

    total_records: Mapped[int] = mapped_column(Integer, server_default="0")
    processed_records: Mapped[int] = mapped_column(Integer, server_default="0")
    inserted_records: Mapped[int] = mapped_column(Integer, server_default="0")
    updated_records: Mapped[int] = mapped_column(Integer, server_default="0")
    failed_records: Mapped[int] = mapped_column(Integer, server_default="0")

    error_message: Mapped[Optional[str]] = mapped_column(Text)

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
    )

    logs: Mapped[List["PipelineLog"]] = relationship(
        "PipelineLog",
        back_populates="pipeline_run",
        cascade="all, delete-orphan",
    )