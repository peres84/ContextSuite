"""A2A task result — the final outcome returned after execution."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from contextsuite_shared.a2a.task import Artifact, TaskState


class TaskResult(BaseModel):
    """Final result returned from the CLI Agent after execution."""

    task_id: str = Field(description="A2A task ID")
    state: TaskState = Field(description="Final state: completed or failed")
    summary: str | None = Field(default=None, description="Human-readable result summary")
    output: str | None = Field(default=None, description="Raw output from the coding assistant")
    artifacts: list[Artifact] = Field(default_factory=list)
    duration_seconds: float | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # ContextSuite extensions
    run_id: str | None = Field(default=None, description="ContextSuite run ID")
    trace_id: str | None = Field(default=None, description="Distributed trace ID")
