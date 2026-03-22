"""ContextSuite-specific task payload carried inside A2A messages.

This is the structured data we put in a DataPart when dispatching work
from the Context Agent to the CLI Agent.
"""

from pydantic import BaseModel, Field

from contextsuite_shared.types.approval import RiskLevel


class TaskPayload(BaseModel):
    """ContextSuite task payload — sent as a DataPart in the A2A message."""

    run_id: str = Field(description="ContextSuite run ID for tracing")
    trace_id: str = Field(description="Distributed trace ID")
    prompt: str = Field(description="The approved prompt to execute")
    plan: str | None = Field(default=None, description="Generated or reviewed plan")
    context_summary: str | None = Field(default=None, description="Retrieved context summary")
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="Risk classification")
    assistant: str = Field(default="codex", description="Target coding assistant")
    workspace_path: str | None = Field(default=None, description="Target repo path on the client")
    repository: str | None = Field(default=None, description="Repository identifier")
