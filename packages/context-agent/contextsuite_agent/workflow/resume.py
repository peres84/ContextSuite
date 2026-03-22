"""Resume persisted runs after a human approval decision."""

from __future__ import annotations

from datetime import UTC, datetime

from contextsuite_shared.types import ApprovalDecision, ApprovalStatus

from contextsuite_agent.persistence import ApprovalsRepo, PromptsRepo, RunsRepo
from contextsuite_agent.workflow.nodes.classify import classify
from contextsuite_agent.workflow.nodes.dispatch import dispatch
from contextsuite_agent.workflow.nodes.memory import save_memory
from contextsuite_agent.workflow.nodes.package import prepare_dispatch
from contextsuite_agent.workflow.state import AgentState


def load_state_for_run(run_id: str) -> AgentState:
    """Rebuild workflow state from persisted records for a run."""
    run = RunsRepo.get_run(run_id)
    if not run:
        raise ValueError(f"Run not found: {run_id}")

    prompt_record = PromptsRepo.get_prompt_for_run(run_id)
    plan_record = RunsRepo.get_latest_plan(run_id)
    snapshot_record = RunsRepo.get_latest_context_snapshot(run_id)

    if not prompt_record:
        raise ValueError(f"Prompt not found for run: {run_id}")

    state: AgentState = {
        "run_id": run_id,
        "trace_id": str(run["trace_id"]),
        "prompt": prompt_record["content"],
        "assistant": run.get("assistant", prompt_record.get("assistant", "codex")),
        "repository_id": run.get("repository_id"),
        "plan": plan_record["content"] if plan_record else None,
        "context_summary": snapshot_record["summary"] if snapshot_record else None,
        "context_sources": snapshot_record["sources"] if snapshot_record else [],
    }
    return classify(state)


def resolve_human_approval(
    *,
    run_id: str,
    approved: bool,
    reviewer: str,
    reason: str | None = None,
    workspace_path: str | None = None,
) -> AgentState:
    """Resolve an escalated run with a human decision and continue if approved."""
    state = load_state_for_run(run_id)
    status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED

    decision = ApprovalDecision(
        approved=approved,
        status=status,
        risk=state["risk"],
        reason=reason or (
            "Human approved after review"
            if approved
            else "Human rejected after review"
        ),
        reviewer=reviewer,
        policy_violations=[],
        timestamp=datetime.now(UTC),
    )

    ApprovalsRepo.create_approval(
        run_id=run_id,
        decision=str(status),
        risk=str(state["risk"].level),
        reason=decision.reason,
        reviewer=reviewer,
        policy_violations=[],
    )

    state["approval"] = decision
    if workspace_path:
        state["workspace_path"] = workspace_path

    if not approved:
        RunsRepo.update_run_status(run_id, "rejected")
        return {**state, "dispatch_status": "rejected_by_human"}

    RunsRepo.update_run_status(run_id, "approved")
    state = prepare_dispatch(state)
    state = dispatch(state)
    state = save_memory(state)
    return state
