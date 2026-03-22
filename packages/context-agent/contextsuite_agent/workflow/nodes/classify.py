"""Risk classification node — assesses task risk level."""

from __future__ import annotations

import logging
import re

from contextsuite_shared.types import RiskAssessment, RiskSignal

from contextsuite_agent.persistence import RunsRepo
from contextsuite_agent.workflow.state import AgentState

logger = logging.getLogger(__name__)

COLOR_NAMES = (
    "green",
    "red",
    "blue",
    "orange",
    "yellow",
    "purple",
    "teal",
    "black",
    "white",
)
COLOR_PATTERN = "|".join(COLOR_NAMES)

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

REQUIRED_COLOR_PATTERNS = [
    re.compile(
        rf"(?:primary|brand|theme)[^.\n]{{0,80}}?"
        rf"(?:must|should)\s+(?:remain|stay|be|keep)[^.\n]{{0,20}}?"
        rf"\b(?P<color>{COLOR_PATTERN})\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"(?:must|should)\s+(?:keep|remain|stay)[^.\n]{{0,40}}?"
        rf"(?:primary|brand|theme)?[^.\n]{{0,20}}?"
        rf"\b(?P<color>{COLOR_PATTERN})\b",
        re.IGNORECASE,
    ),
]

REQUESTED_COLOR_PATTERNS = [
    re.compile(
        rf"(?:change|switch|turn|make|update|restyle|set|replace)[^.\n]{{0,80}}?"
        rf"\b(?:to|into|as)\s+(?P<color>{COLOR_PATTERN})\b",
        re.IGNORECASE,
    ),
    re.compile(
        rf"\b(?P<color>{COLOR_PATTERN})\b[^.\n]{{0,40}}?"
        rf"\b(?:theme|palette|styling|brand|buttons?|cta|hero|accent)\b",
        re.IGNORECASE,
    ),
]


def _iter_context_texts(context_sources: list[dict] | None) -> list[str]:
    texts: list[str] = []
    for source in context_sources or []:
        parts: list[str] = []
        content = source.get("content")
        if content:
            parts.append(str(content))

        metadata = source.get("metadata") or {}
        for key in ("title", "file", "source"):
            value = metadata.get(key)
            if value:
                parts.append(str(value))

        if parts:
            texts.append(" ".join(parts).lower())
    return texts


def _extract_required_brand_color(context_sources: list[dict] | None) -> str | None:
    for text in _iter_context_texts(context_sources):
        if not any(keyword in text for keyword in ("brand color", "primary color", "theme")):
            continue
        for pattern in REQUIRED_COLOR_PATTERNS:
            match = pattern.search(text)
            if match:
                return match.group("color").lower()
    return None


def _extract_requested_colors(text: str) -> list[str]:
    requested: list[str] = []
    for pattern in REQUESTED_COLOR_PATTERNS:
        for match in pattern.finditer(text):
            color = match.group("color").lower()
            if color not in requested:
                requested.append(color)
    return requested


def _detect_context_constraint_signals(state: AgentState, prompt_text: str) -> list[RiskSignal]:
    required_color = _extract_required_brand_color(state.get("context_sources"))
    if not required_color:
        return []

    requested_colors = _extract_requested_colors(prompt_text)
    conflicting = [color for color in requested_colors if color != required_color]
    if not conflicting:
        return []

    requested_summary = ", ".join(conflicting)
    return [
        RiskSignal(
            signal=(
                "violates retrieved constraint: primary brand color must remain "
                f"{required_color}; requested {requested_summary}"
            ),
            weight=0.9,
        )
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

    # Check for direct contradictions against retrieved constraints.
    signals.extend(_detect_context_constraint_signals(state, prompt))

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

    try:
        RunsRepo.update_run_status(run_id, "reviewing", risk=level)
    except Exception:
        logger.debug("classify: could not persist risk for run=%s", run_id, exc_info=True)

    return {**state, "risk": risk}
