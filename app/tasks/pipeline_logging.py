from typing import Any, Optional

from app.models import PipelineLog


def add_pipeline_log(
    db,
    pipeline_run_id: Optional[int],
    level: str,
    message: str,
    context: Optional[Any] = None,
) -> None:
    if pipeline_run_id is None:
        return

    db.add(
        PipelineLog(
            pipeline_run_id=pipeline_run_id,
            level=level,
            message=message,
            context=context,
        )
    )