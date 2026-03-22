"""Risk classification node — assesses task risk level."""

from __future__ import annotations

import logging
import re

from contextsuite_shared.types import RiskAssessment, RiskSignal

from contextsuite_agent.workflow.state import AgentState

logger = logging.getLogger(__name__)

# Patterns that indicate higher risk
HIGH_RISK_PATTERNS = [
    (r"\bdelete\b", "destructive operation: delete"),
    (r"\bdrop\b", "destructive operation: drop"),
    (r"\bremove all\b", "destructive operation: remove all"),
    (r"\bforce push\b", "destructive operation: force push"),
    (r"\bproduction\b", "targets production environment"),
    (r"\bmigrat", "database migration"),
    (r"\bsecret\b", "involves secrets or credentials"),
    (r"\bauth", "involves authentication"),
    (r"\bpayment\b", "involves payment processing"),
    (r"\bbilling\b", "involves billing"),
]

MEDIUM_RISK_PATTERNS = [
    (r"\brefactor\b", "refactoring existing code"),
    (r"\bupdate\b.*\bdepend", "updating dependencies"),
    (r"\bapi\b", "modifying API surface"),
    (r"\bschema\b", "schema changes"),
    (r"\bconfig\b", "configuration changes"),
]


def classify(state: AgentState) -> AgentState:
    """Classify the risk level of the task based on prompt, plan, and context."""
    prompt = state["prompt"].lower()
    plan_text = (state.get("plan") or "").lower()
    run_id = state["run_id"]
    combined = f"{prompt} {plan_text}"

    signals: list[RiskSignal] = []

    # Check high-risk patterns
    for pattern, description in HIGH_RISK_PATTERNS:
        if re.search(pattern, combined):
            signals.append(RiskSignal(signal=description, weight=0.8))

    # Check medium-risk patterns
    for pattern, description in MEDIUM_RISK_PATTERNS:
        if re.search(pattern, combined):
            signals.append(RiskSignal(signal=description, weight=0.4))

    # Determine level
    max_weight = max((s.weight for s in signals), default=0.0)
    if max_weight >= 0.7:
        level = "high"
    elif max_weight >= 0.3 or len(signals) >= 3:
        level = "medium"
    else:
        level = "low"

    reason = "; ".join(s.signal for s in signals) if signals else "no risk signals detected"

    risk = RiskAssessment(level=level, signals=signals, reason=reason)
    logger.info("classify: run=%s risk=%s (%d signals)", run_id, level, len(signals))

    return {**state, "risk": risk}
