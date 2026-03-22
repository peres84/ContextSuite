"""Tests for workflow nodes that don't require external services."""

from contextsuite_agent.workflow.nodes.classify import classify
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
        # "auth" in plan triggers medium risk
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
