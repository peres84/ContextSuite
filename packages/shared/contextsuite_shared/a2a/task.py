"""A2A task, message, and part schemas aligned to the protocol spec."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TaskState(StrEnum):
    """A2A task lifecycle states."""

    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"
    REJECTED = "rejected"
    AUTH_REQUIRED = "auth-required"
    UNKNOWN = "unknown"


class Role(StrEnum):
    """Sender role for A2A messages."""

    USER = "user"
    AGENT = "agent"


def _normalize_kind(value: Any, default: str) -> Any:
    if not isinstance(value, dict):
        return value
    normalized = dict(value)
    if "kind" not in normalized and "type" in normalized:
        normalized["kind"] = normalized.pop("type")
    normalized.setdefault("kind", default)
    return normalized


class TextPart(BaseModel):
    """Plain text content."""

    kind: Literal["text"] = "text"
    text: str
    metadata: dict[str, Any] | None = None

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_shape(cls, value: Any) -> Any:
        return _normalize_kind(value, "text")

    @property
    def type(self) -> str:
        """Legacy alias retained for backwards compatibility."""
        return self.kind


class FileWithBytes(BaseModel):
    """Inline file bytes encoded as base64 text."""

    bytes: str
    name: str | None = None
    mime_type: str | None = Field(default=None, alias="mimeType")

    model_config = ConfigDict(populate_by_name=True)


class FileWithUri(BaseModel):
    """File reference by URI."""

    uri: str
    name: str | None = None
    mime_type: str | None = Field(default=None, alias="mimeType")

    model_config = ConfigDict(populate_by_name=True)


FileContent = FileWithBytes | FileWithUri


class FilePart(BaseModel):
    """File reference or inline file content."""

    kind: Literal["file"] = "file"
    file: FileContent
    metadata: dict[str, Any] | None = None

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_shape(cls, value: Any) -> Any:
        normalized = _normalize_kind(value, "file")
        if not isinstance(normalized, dict) or "file" in normalized:
            return normalized

        file_payload: dict[str, Any] = {}
        if "uri" in normalized:
            file_payload["uri"] = normalized.pop("uri")
        if "bytes" in normalized:
            file_payload["bytes"] = normalized.pop("bytes")

        name = normalized.pop("name", None)
        mime_type = (
            normalized.pop("mimeType", None)
            or normalized.pop("mediaType", None)
            or normalized.pop("media_type", None)
            or normalized.pop("mime_type", None)
        )
        if name is not None:
            file_payload["name"] = name
        if mime_type is not None:
            file_payload["mimeType"] = mime_type

        normalized["file"] = file_payload
        return normalized

    @property
    def type(self) -> str:
        """Legacy alias retained for backwards compatibility."""
        return self.kind


class DataPart(BaseModel):
    """Structured JSON data."""

    kind: Literal["data"] = "data"
    data: dict[str, Any]
    metadata: dict[str, Any] | None = None

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_shape(cls, value: Any) -> Any:
        return _normalize_kind(value, "data")

    @property
    def type(self) -> str:
        """Legacy alias retained for backwards compatibility."""
        return self.kind


Part = Annotated[TextPart | FilePart | DataPart, Field(discriminator="kind")]


class Message(BaseModel):
    """A single message exchanged between a client and an agent."""

    kind: Literal["message"] = "message"
    role: Role
    parts: list[Part]
    message_id: str = Field(default_factory=lambda: uuid4().hex, alias="messageId")
    task_id: str | None = Field(default=None, alias="taskId")
    context_id: str | None = Field(default=None, alias="contextId")
    metadata: dict[str, Any] | None = None
    extensions: list[str] | None = None
    reference_task_ids: list[str] | None = Field(default=None, alias="referenceTaskIds")

    model_config = ConfigDict(populate_by_name=True)


class Artifact(BaseModel):
    """An output artifact produced by a task."""

    artifact_id: str = Field(default_factory=lambda: uuid4().hex, alias="artifactId")
    name: str | None = None
    description: str | None = None
    parts: list[Part] = Field(default_factory=list)
    metadata: dict[str, Any] | None = None
    extensions: list[str] | None = None

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_shape(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        normalized = dict(value)
        if "artifactId" not in normalized and "id" in normalized:
            normalized["artifactId"] = normalized.pop("id")
        if "name" not in normalized and "title" in normalized:
            normalized["name"] = normalized.pop("title")
        return normalized

    @property
    def id(self) -> str:
        """Legacy alias retained for backwards compatibility."""
        return self.artifact_id

    @property
    def title(self) -> str | None:
        """Legacy alias retained for backwards compatibility."""
        return self.name


class TaskStatus(BaseModel):
    """Current status of an A2A task."""

    state: TaskState
    message: Message | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_shape(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        normalized = dict(value)
        message = normalized.get("message")
        if isinstance(message, str):
            normalized["message"] = Message(
                role=Role.AGENT,
                parts=[TextPart(text=message)],
            )
        return normalized


class Task(BaseModel):
    """A2A Task — the stateful unit of work exchanged between agents."""

    kind: Literal["task"] = "task"
    id: str = Field(description="Server-generated unique task identifier")
    context_id: str = Field(alias="contextId", description="Conversation context identifier")
    status: TaskStatus
    history: list[Message] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    metadata: dict[str, Any] | None = None

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_shape(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        normalized = dict(value)
        if "history" not in normalized and "messages" in normalized:
            normalized["history"] = normalized.pop("messages")
        return normalized

    @property
    def messages(self) -> list[Message]:
        """Legacy alias retained for backwards compatibility."""
        return self.history
