"""Graph state definition for the Context Agent workflow."""

from __future__ import annotations

from typing import Any, TypedDict

from contextsuite_shared.types import ApprovalDecision, RiskAssessment


class AgentState(TypedDict, total=False):
    """State passed through the LangGraph workflow."""

    # Input
    prompt: str
    repository: str | None
    assistant: str

    # Run tracking
    run_id: str
    trace_id: str
    repository_id: str | None

    # Workflow outputs
    context_summary: str | None
    plan: str | None
    risk: RiskAssessment | None
    approval: ApprovalDecision | None

    # Dispatch
    task_id: str | None
    payload: Any  # TaskPayload when ready
    dispatch_status: str | None
