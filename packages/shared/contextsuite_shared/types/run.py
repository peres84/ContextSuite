"""Run and trace ID types."""

import uuid

from pydantic import BaseModel, Field


def _new_id() -> str:
    return uuid.uuid4().hex


class RunMeta(BaseModel):
    """Metadata for a single run through the system."""

    run_id: str = Field(default_factory=_new_id, description="Unique run identifier")
    trace_id: str = Field(default_factory=_new_id, description="Trace ID for observability")
    repository: str | None = Field(default=None, description="Target repository identifier")
