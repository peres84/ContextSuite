"""Tests for workflow nodes that don't require external services."""

from contextsuite_agent.workflow.nodes.approve import approve
from contextsuite_agent.workflow.nodes.classify import classify
from contextsuite_agent.workflow.nodes.memory import (
    extract_memory_references,
    should_persist_issue_memory,
)
from contextsuite_agent.workflow.state import AgentState


class TestClassify:
    def _make_state(self, prompt: str, plan: str = "") -> AgentState:
        return AgentState(
            prompt=prompt,
            run_id="test-run",
            trace_id="test-trace",
            plan=plan,
        )

    def test_low_risk_simple_task(self):
        state = self._make_state("add a utility function to format dates")
        result = classify(state)
        assert result["risk"].level == "low"

    def test_high_risk_delete(self):
        state = self._make_state("delete the old payment records from the database")
        result = classify(state)
        assert result["risk"].level == "high"
        assert any("delete" in s.signal for s in result["risk"].signals)

    def test_high_risk_production(self):
        state = self._make_state("deploy this fix to production immediately")
        result = classify(state)
        assert result["risk"].level == "high"

    def test_medium_risk_refactor(self):
        state = self._make_state("refactor the webhook handler")
        result = classify(state)
        assert result["risk"].level == "medium"

    def test_medium_risk_api_change(self):
        state = self._make_state("change the API response format for /users")
        result = classify(state)
        assert result["risk"].level == "medium"

    def test_risk_from_plan_text(self):
        state = self._make_state(
            prompt="fix the bug",
            plan="Steps: 1. Modify the authentication module to handle edge case",
        )
        result = classify(state)
        assert result["risk"].level in ("medium", "high")

    def test_payment_is_high_risk(self):
        state = self._make_state("update the payment processing logic")
        result = classify(state)
        assert result["risk"].level == "high"

    def test_multiple_signals(self):
        state = self._make_state("delete and drop the old auth schema in production")
        result = classify(state)
        assert result["risk"].level == "high"
        assert len(result["risk"].signals) >= 3

    def test_high_risk_when_prompt_conflicts_with_retrieved_brand_constraint(self):
        state = AgentState(
            prompt="Refresh the landing page styling and change the primary color to red.",
            run_id="test-run",
            trace_id="test-trace",
            context_sources=[
                {
                    "source": "vector",
                    "content": (
                        "Constraint: The primary brand color must remain green. "
                        "Do not switch the global theme from green to red."
                    ),
                    "metadata": {
                        "title": "Constraint: primary brand color must stay green",
                    },
                }
            ],
        )

        result = classify(state)
        assert result["risk"].level == "high"
        assert any(
            "primary brand color must remain green" in signal.signal
            for signal in result["risk"].signals
        )

    def test_does_not_flag_when_prompt_keeps_required_brand_color(self):
        state = AgentState(
            prompt="Improve spacing and typography but keep the primary green theme.",
            run_id="test-run",
            trace_id="test-trace",
            context_sources=[
                {
                    "source": "vector",
                    "content": "Constraint: The primary brand color must remain green.",
                    "metadata": {
                        "title": "Constraint: primary brand color must stay green",
                    },
                }
            ],
        )

        result = classify(state)
        assert result["risk"].level == "low"
        assert not any(
            "violates retrieved constraint" in signal.signal for signal in result["risk"].signals
        )

    def test_does_not_flag_when_only_plan_mentions_forbidden_color_as_warning(self):
        state = AgentState(
            prompt="Improve spacing and typography but keep the primary green theme.",
            plan=(
                "Keep the primary green theme. Do not change the global theme from green "
                "to red."
            ),
            run_id="test-run",
            trace_id="test-trace",
            context_sources=[
                {
                    "source": "vector",
                    "content": "Constraint: The primary brand color must remain green.",
                    "metadata": {
                        "title": "Constraint: primary brand color must stay green",
                    },
                }
            ],
        )

        result = classify(state)
        assert result["risk"].level == "low"
        assert not any(
            "violates retrieved constraint" in signal.signal for signal in result["risk"].signals
        )


class TestApprove:
    def test_high_risk_escalates_for_human_review(self, monkeypatch):
        monkeypatch.setattr(
            "contextsuite_agent.workflow.nodes.approve.RunsRepo.update_run_status",
            lambda *args, **kwargs: {},
        )
        created = {}

        def fake_create_approval(**kwargs):
            created.update(kwargs)
            return kwargs

        monkeypatch.setattr(
            "contextsuite_agent.workflow.nodes.approve.ApprovalsRepo.create_approval",
            fake_create_approval,
        )

        state = AgentState(
            prompt="delete payment data in production",
            run_id="test-run",
            trace_id="test-trace",
            risk=classify(
                AgentState(
                    prompt="delete payment data in production",
                    run_id="test-run",
                    trace_id="test-trace",
                )
            )["risk"],
        )

        result = approve(state)
        assert result["approval"].status == "escalated"
        assert not result["approval"].approved
        assert result["dispatch_status"] == "pending_human_approval"
        assert created["decision"] == "escalated"

    def test_policy_violation_sets_blocked_status(self, monkeypatch):
        monkeypatch.setattr(
            "contextsuite_agent.workflow.nodes.approve.RunsRepo.update_run_status",
            lambda *args, **kwargs: {},
        )
        monkeypatch.setattr(
            "contextsuite_agent.workflow.nodes.approve.ApprovalsRepo.create_approval",
            lambda **kwargs: kwargs,
        )

        state = AgentState(
            prompt="drop database tables and start fresh",
            run_id="test-run",
            trace_id="test-trace",
            risk=classify(
                AgentState(
                    prompt="drop database tables and start fresh",
                    run_id="test-run",
                    trace_id="test-trace",
                )
            )["risk"],
        )

        result = approve(state)
        assert result["approval"].status == "rejected"
        assert result["dispatch_status"] == "skipped_not_approved"


class TestMemoryExtraction:
    def test_extracts_issue_and_constraint_refs(self):
        issues, constraints = extract_memory_references([
            {
                "source": "vector",
                "content": "Past incident INC-2024-0142 caused duplicate charges.",
                "metadata": {
                    "type": "incident",
                    "title": "INC-2024-0142 duplicate charges",
                    "file": "incidents/INC-2024-0142.md",
                },
            },
            {
                "source": "graph",
                "content": "Constraint: webhook timeout",
                "metadata": {
                    "constraint_id": "ADR-012",
                    "source": "adr/ADR-012.md",
                },
            },
        ])

        assert issues[0]["id"] == "INC-2024-0142"
        assert constraints[0]["id"] == "ADR-012"

    def test_persists_only_when_issue_related(self):
        assert not should_persist_issue_memory(
            issue_refs=[],
            constraint_refs=[],
            outcome_state="completed",
            policy_violations=[],
        )
        assert should_persist_issue_memory(
            issue_refs=[{"id": "INC-2024-0142"}],
            constraint_refs=[],
            outcome_state="completed",
            policy_violations=[],
        )
