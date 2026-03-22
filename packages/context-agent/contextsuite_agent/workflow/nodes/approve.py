"""Approval routing node — auto-approve low risk, flag medium/high for review."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from contextsuite_shared.types import ApprovalDecision, ApprovalStatus, RiskAssessment

from contextsuite_agent.persistence import ApprovalsRepo, RunsRepo
from contextsuite_agent.workflow.state import AgentState

logger = logging.getLogger(__name__)

# Policy rules — prompts matching these are always blocked
BLOCKED_PATTERNS: list[str] = [
    "drop database",
    "rm -rf /",
    "delete all users",
    "disable authentication",
]


def approve(state: AgentState) -> AgentState:
    """Route the task through approval based on risk level and policy checks."""
    run_id = state["run_id"]
    risk_assessment: RiskAssessment = state.get("risk") or RiskAssessment()
    prompt = state["prompt"].lower()
    plan_text = (state.get("plan") or "").lower()
    combined = f"{prompt} {plan_text}"

    risk_level = risk_assessment.level
    dispatch_status = state.get("dispatch_status")

    # Policy check — blocked patterns
    violations = []
    for pattern in BLOCKED_PATTERNS:
        if pattern in combined:
            violations.append(f"blocked pattern: '{pattern}'")

    if violations:
        decision = ApprovalDecision(
            approved=False,
            status=ApprovalStatus.REJECTED,
            risk=risk_assessment,
            reason=f"Policy violation: {'; '.join(violations)}",
            reviewer="auto-policy",
            policy_violations=violations,
            timestamp=datetime.now(UTC),
        )
        RunsRepo.update_run_status(run_id, "rejected")
        logger.warning("approve: run=%s REJECTED (policy violation)", run_id)
        dispatch_status = "skipped_not_approved"
    elif risk_level == "low":
        decision = ApprovalDecision(
            approved=True,
            status=ApprovalStatus.APPROVED,
            risk=risk_assessment,
            reason="Auto-approved: low risk task",
            reviewer="auto",
            policy_violations=[],
            timestamp=datetime.now(UTC),
        )
        RunsRepo.update_run_status(run_id, "approved")
        logger.info("approve: run=%s auto-approved (low risk)", run_id)
    elif risk_level == "medium":
        decision = ApprovalDecision(
            approved=True,
            status=ApprovalStatus.APPROVED,
            risk=risk_assessment,
            reason="Auto-approved: medium risk (MVP mode)",
            reviewer="auto-mvp",
            policy_violations=[],
            timestamp=datetime.now(UTC),
        )
        RunsRepo.update_run_status(run_id, "approved")
        logger.info("approve: run=%s auto-approved (medium risk, MVP mode)", run_id)
    else:
        decision = ApprovalDecision(
            approved=False,
            status=ApprovalStatus.ESCALATED,
            risk=risk_assessment,
            reason="Requires human approval: high risk task",
            reviewer="auto",
            policy_violations=[],
            timestamp=datetime.now(UTC),
        )
        RunsRepo.update_run_status(run_id, "reviewing")
        logger.warning("approve: run=%s ESCALATED (high risk, needs human approval)", run_id)
        dispatch_status = "pending_human_approval"

    # Persist approval
    ApprovalsRepo.create_approval(
        run_id=run_id,
        decision=str(decision.status),
        risk=str(risk_level),
        reason=decision.reason,
        reviewer=decision.reviewer,
        policy_violations=decision.policy_violations,
    )

    next_state = {**state, "approval": decision}
    if dispatch_status:
        next_state["dispatch_status"] = dispatch_status
    return next_state
