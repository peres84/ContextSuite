"""Approval and risk-level types."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskSignal(BaseModel):
    """A single signal that contributed to the risk classification."""

    signal: str = Field(description="What was detected")
    weight: float = Field(default=1.0, description="How much this contributes to risk")


class RiskAssessment(BaseModel):
    """Full risk assessment for a task."""

    level: RiskLevel = RiskLevel.LOW
    signals: list[RiskSignal] = Field(default_factory=list)
    reason: str | None = Field(default=None, description="Summary of why this risk level was set")


class ApprovalDecision(BaseModel):
    """Represents an approval or rejection decision."""

    approved: bool
    risk: RiskAssessment = Field(default_factory=RiskAssessment)
    reason: str | None = Field(default=None, description="Why the task was approved or blocked")
    reviewer: str = Field(default="auto", description="Who approved: 'auto' or a user ID")
    policy_violations: list[str] = Field(
        default_factory=list, description="List of violated policy rules"
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
