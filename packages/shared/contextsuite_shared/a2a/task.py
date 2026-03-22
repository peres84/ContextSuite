"""A2A task and message schemas following the A2A protocol spec."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class TaskState(StrEnum):
    """A2A task lifecycle states."""

    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    REJECTED = "rejected"
    INPUT_REQUIRED = "input_required"
    AUTH_REQUIRED = "auth_required"


class Role(StrEnum):
    USER = "user"
    AGENT = "agent"


# --- Parts (A2A message content) ---


class TextPart(BaseModel):
    """Plain text content."""

    type: str = "text"
    text: str
    media_type: str = Field(default="text/plain", alias="mediaType")

    model_config = {"populate_by_name": True}


class FilePart(BaseModel):
    """File reference."""

    type: str = "file"
    uri: str
    media_type: str = Field(alias="mediaType")
    name: str | None = None
    size_bytes: int | None = Field(default=None, alias="sizeBytes")

    model_config = {"populate_by_name": True}


class DataPart(BaseModel):
    """Structured JSON data."""

    type: str = "data"
    data: dict
    schema_id: str | None = Field(default=None, alias="schema")

    model_config = {"populate_by_name": True}


Part = TextPart | FilePart | DataPart


# --- Message ---


class Message(BaseModel):
    """A single message in the A2A conversation."""

    id: str | None = None
    role: Role
    parts: list[Part]
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        alias="createdAt",
    )
    metadata: dict | None = None

    model_config = {"populate_by_name": True}


# --- Artifact ---


class Artifact(BaseModel):
    """An output artifact produced by task execution."""

    id: str
    title: str | None = None
    mime_type: str | None = Field(default=None, alias="mimeType")
    parts: list[Part] = Field(default_factory=list)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        alias="createdAt",
    )
    metadata: dict | None = None

    model_config = {"populate_by_name": True}


# --- Task ---


class TaskStatus(BaseModel):
    """Current status of an A2A task."""

    state: TaskState
    message: str | None = None
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )


class Task(BaseModel):
    """A2A Task — the core unit of work exchanged between agents."""

    id: str = Field(description="Server-generated unique task identifier")
    context_id: str | None = Field(
        default=None, alias="contextId", description="Groups related tasks"
    )
    status: TaskStatus
    messages: list[Message] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        alias="createdAt",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        alias="updatedAt",
    )
    metadata: dict | None = None

    model_config = {"populate_by_name": True}
