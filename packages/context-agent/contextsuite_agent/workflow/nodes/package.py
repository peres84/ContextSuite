"""Task packaging node — builds the A2A payload for dispatch to the CLI Agent."""

from __future__ import annotations

import logging
import uuid

from contextsuite_shared.a2a import TaskPayload

from contextsuite_agent.persistence import RunsRepo
from contextsuite_agent.workflow.state import AgentState

logger = logging.getLogger(__name__)


def package(state: AgentState) -> AgentState:
    """Package the approved task into an A2A TaskPayload for dispatch."""
    run_id = state["run_id"]
    trace_id = state["trace_id"]
    approval = state.get("approval")

    if not approval or not approval.approved:
        logger.info("package: skipping — task not approved (run=%s)", run_id)
        RunsRepo.update_run_status(run_id, "rejected")
        return {**state, "dispatch_status": "skipped_not_approved"}

    task_id = uuid.uuid4().hex
    logger.info("package: building A2A payload for run=%s task=%s", run_id, task_id)

    payload = TaskPayload(
        run_id=run_id,
        trace_id=trace_id,
        prompt=state["prompt"],
        plan=state.get("plan"),
        context_summary=state.get("context_summary"),
        risk_level=state["risk"].level if state.get("risk") else "low",
        assistant=state.get("assistant", "codex"),
        repository=state.get("repository"),
    )

    # Move run to dispatched
    RunsRepo.update_run_status(run_id, "dispatched")

    logger.info("package: ready to dispatch task=%s via A2A (run=%s)", task_id, run_id)

    return {
        **state,
        "task_id": task_id,
        "payload": payload,
        "dispatch_status": "ready",
    }
