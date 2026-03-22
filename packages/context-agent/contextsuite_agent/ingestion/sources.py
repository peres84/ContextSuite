"""Input source definitions for context ingestion."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class SourceType(StrEnum):
    """Types of documents the ingestion pipeline accepts."""

    INCIDENT = "incident"
    ADR = "adr"
    CONSTRAINT = "constraint"
    DOC = "doc"
    CODE_SUMMARY = "code_summary"
    ISSUE = "issue"


class DocumentSource(BaseModel):
    """A document to be ingested into the context store."""

    content: str
    source_type: SourceType
    title: str | None = None
    source_path: str | None = None
    repository: str | None = None
    repository_id: str | None = None
    metadata: dict | None = None
