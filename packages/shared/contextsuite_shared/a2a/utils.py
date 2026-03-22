"""Helpers for converting between ContextSuite data and A2A protocol objects."""

from __future__ import annotations

from typing import Any

from contextsuite_shared.a2a.task import Artifact, DataPart, Message, Role, TextPart


def extract_text(message: Message | None) -> str:
    """Concatenate text parts from an A2A message."""
    if message is None:
        return ""
    chunks = [part.text for part in message.parts if isinstance(part, TextPart) and part.text]
    return "\n".join(chunks).strip()


def extract_data(message: Message | None) -> list[dict[str, Any]]:
    """Collect structured data parts from an A2A message."""
    if message is None:
        return []
    return [part.data for part in message.parts if isinstance(part, DataPart)]


def message_from_text(
    text: str,
    *,
    role: Role,
    task_id: str | None = None,
    context_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Message:
    """Create a simple text message."""
    return Message(
        role=role,
        parts=[TextPart(text=text)],
        taskId=task_id,
        contextId=context_id,
        metadata=metadata,
    )


def artifact_from_text(
    text: str,
    *,
    name: str = "result",
    description: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Artifact:
    """Create a simple text artifact."""
    return Artifact(
        name=name,
        description=description,
        parts=[TextPart(text=text)],
        metadata=metadata,
    )


def model_dump(value: Any) -> Any:
    """Dump Pydantic models using aliases when available."""
    if hasattr(value, "model_dump"):
        return value.model_dump(by_alias=True, exclude_none=True)
    return value
