"""A2A task status update — sent via SSE or push notification."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from contextsuite_shared.a2a.task import TaskState


class TaskStatusUpdate(BaseModel):
    """Status update pushed from the CLI Agent back to the Context Agent."""

    task_id: str = Field(description="A2A task ID")
    state: TaskState
    message: str | None = Field(default=None, description="Human-readable status message")
    progress: float | None = Field(
        default=None, description="Progress 0.0-1.0 if available", ge=0.0, le=1.0
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # ContextSuite extensions
    run_id: str | None = Field(default=None, description="ContextSuite run ID")
    trace_id: str | None = Field(default=None, description="Distributed trace ID")
