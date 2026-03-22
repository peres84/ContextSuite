"""A2A task status update event models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from contextsuite_shared.a2a.task import TaskStatus


class TaskStatusUpdate(BaseModel):
    """A2A status update event used by streaming transports."""

    kind: Literal["status-update"] = "status-update"
    task_id: str = Field(alias="taskId")
    context_id: str = Field(alias="contextId")
    status: TaskStatus
    final: bool = False
    metadata: dict[str, Any] | None = None

    model_config = ConfigDict(populate_by_name=True)
