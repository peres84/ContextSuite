"""A2A error payload for failed or rejected tasks."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ErrorCode(StrEnum):
    """Machine-readable error codes."""

    EXECUTION_FAILED = "execution_failed"
    ADAPTER_NOT_FOUND = "adapter_not_found"
    WORKSPACE_NOT_FOUND = "workspace_not_found"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    POLICY_BLOCKED = "policy_blocked"
    APPROVAL_DENIED = "approval_denied"
    INTERNAL_ERROR = "internal_error"


class TaskError(BaseModel):
    """Error payload for failed or blocked tasks."""

    task_id: str = Field(description="A2A task ID")
    error_code: ErrorCode
    message: str = Field(description="Human-readable error description")
    reason: str | None = Field(default=None, description="Detailed reason for the error")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # ContextSuite extensions
    run_id: str | None = Field(default=None, description="ContextSuite run ID")
    trace_id: str | None = Field(default=None, description="Distributed trace ID")
