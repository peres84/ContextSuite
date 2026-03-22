"""Tests for A2A contract schemas and shared types."""

import json

import pytest
from contextsuite_shared.a2a import (
    Artifact,
    DataPart,
    ErrorCode,
    FilePart,
    Message,
    Role,
    Task,
    TaskError,
    TaskPayload,
    TaskResult,
    TaskState,
    TaskStatus,
    TaskStatusUpdate,
    TextPart,
)
from contextsuite_shared.agent_card import (
    build_cli_agent_card,
    build_context_agent_card,
)
from contextsuite_shared.types import (
    ApprovalDecision,
    ApprovalStatus,
    PromptInput,
    RiskAssessment,
    RiskLevel,
    RiskSignal,
    RunMeta,
)

# --- A2A Task lifecycle ---


class TestTaskState:
    def test_all_states_exist(self):
        expected = {
            "working",
            "completed",
            "failed",
            "canceled",
            "rejected",
            "input_required",
            "auth_required",
        }
        assert {s.value for s in TaskState} == expected


class TestTask:
    def test_minimal_task(self):
        task = Task(id="t-1", status=TaskStatus(state=TaskState.WORKING))
        assert task.id == "t-1"
        assert task.status.state == TaskState.WORKING
        assert task.messages == []
        assert task.artifacts == []

    def test_task_with_messages(self):
        msg = Message(role=Role.USER, parts=[TextPart(text="fix the bug")])
        task = Task(
            id="t-2",
            status=TaskStatus(state=TaskState.WORKING),
            messages=[msg],
        )
        assert len(task.messages) == 1
        assert task.messages[0].parts[0].text == "fix the bug"

    def test_task_roundtrip_json(self):
        task = Task(
            id="t-3",
            status=TaskStatus(state=TaskState.COMPLETED, message="done"),
            messages=[Message(role=Role.AGENT, parts=[TextPart(text="fixed")])],
            artifacts=[Artifact(id="a-1", title="patch", parts=[TextPart(text="diff")])],
        )
        data = json.loads(task.model_dump_json(by_alias=True))
        assert data["id"] == "t-3"
        assert data["status"]["state"] == "completed"
        assert data["createdAt"] is not None
        restored = Task.model_validate(data)
        assert restored.id == task.id
        assert restored.status.state == task.status.state

    def test_task_context_id(self):
        task = Task(
            id="t-4",
            context_id="ctx-1",
            status=TaskStatus(state=TaskState.WORKING),
        )
        data = task.model_dump(by_alias=True)
        assert data["contextId"] == "ctx-1"


# --- Parts ---


class TestParts:
    def test_text_part(self):
        p = TextPart(text="hello")
        assert p.type == "text"
        assert p.media_type == "text/plain"

    def test_file_part(self):
        p = FilePart(uri="file:///tmp/a.py", media_type="text/x-python", name="a.py")
        assert p.type == "file"
        assert p.name == "a.py"

    def test_data_part(self):
        p = DataPart(data={"key": "value"})
        assert p.type == "data"
        assert p.data["key"] == "value"


# --- TaskPayload (ContextSuite extension) ---


class TestTaskPayload:
    def test_minimal_payload(self):
        p = TaskPayload(run_id="r1", trace_id="t1", prompt="fix the bug")
        assert p.risk_level == RiskLevel.LOW
        assert p.assistant == "codex"

    def test_full_payload(self):
        p = TaskPayload(
            run_id="r1",
            trace_id="t1",
            prompt="add tests",
            plan="1. write tests\n2. run them",
            context_summary="Prior bug in auth module",
            risk_level=RiskLevel.HIGH,
            assistant="claude-code",
            workspace_path="/home/user/repo",
            repository="org/repo",
        )
        assert p.risk_level == RiskLevel.HIGH
        assert p.repository == "org/repo"

    def test_payload_roundtrip(self):
        p = TaskPayload(run_id="r1", trace_id="t1", prompt="test")
        data = json.loads(p.model_dump_json())
        restored = TaskPayload.model_validate(data)
        assert restored.run_id == p.run_id


# --- Status, Result, Error ---


class TestTaskStatusUpdate:
    def test_status_update(self):
        s = TaskStatusUpdate(
            task_id="t-1", state=TaskState.WORKING, message="running", progress=0.5
        )
        assert s.progress == 0.5

    def test_progress_bounds(self):
        with pytest.raises(Exception):
            TaskStatusUpdate(task_id="t-1", state=TaskState.WORKING, progress=1.5)


class TestTaskResult:
    def test_result(self):
        r = TaskResult(
            task_id="t-1",
            state=TaskState.COMPLETED,
            summary="Bug fixed",
            duration_seconds=12.5,
            run_id="r1",
        )
        assert r.state == TaskState.COMPLETED
        assert r.duration_seconds == 12.5


class TestTaskError:
    def test_error(self):
        e = TaskError(
            task_id="t-1",
            error_code=ErrorCode.POLICY_BLOCKED,
            message="Dangerous operation blocked",
            reason="Attempted to delete production database",
        )
        assert e.error_code == ErrorCode.POLICY_BLOCKED

    def test_all_error_codes(self):
        assert len(ErrorCode) == 8


# --- Agent Cards ---


class TestAgentCards:
    def test_context_agent_card(self):
        card = build_context_agent_card("http://localhost:8000")
        assert card.id == "contextsuite-context-agent"
        assert len(card.skills) == 5
        assert card.capabilities.streaming is True
        assert card.capabilities.multi_turn is True

    def test_cli_agent_card(self):
        card = build_cli_agent_card("http://localhost:8001")
        assert card.id == "contextsuite-cli-agent"
        assert len(card.skills) == 3
        assert card.capabilities.multi_turn is False

    def test_agent_card_serialization(self):
        card = build_context_agent_card()
        data = json.loads(card.model_dump_json())
        assert data["name"] == "ContextSuite Context Agent"
        assert isinstance(data["skills"], list)


# --- Approval and Risk ---


class TestApproval:
    def test_auto_approval(self):
        a = ApprovalDecision(approved=True)
        assert a.reviewer == "auto"
        assert a.risk.level == RiskLevel.LOW
        assert a.status == ApprovalStatus.APPROVED

    def test_escalated_status(self):
        a = ApprovalDecision(approved=False, status=ApprovalStatus.ESCALATED)
        assert a.status == ApprovalStatus.ESCALATED
        assert not a.approved

    def test_blocked_with_violations(self):
        a = ApprovalDecision(
            approved=False,
            risk=RiskAssessment(
                level=RiskLevel.HIGH,
                signals=[RiskSignal(signal="deletes production data", weight=3.0)],
                reason="High-risk destructive operation",
            ),
            reason="Policy violation",
            reviewer="user-123",
            policy_violations=["no-prod-deletes"],
        )
        assert not a.approved
        assert len(a.policy_violations) == 1
        assert a.risk.signals[0].weight == 3.0
        assert a.status == ApprovalStatus.REJECTED


class TestRiskLevel:
    def test_all_levels(self):
        assert set(RiskLevel) == {"low", "medium", "high"}


# --- Run and Prompt ---


class TestRunMeta:
    def test_auto_generates_ids(self):
        r = RunMeta()
        assert len(r.run_id) == 32
        assert len(r.trace_id) == 32
        assert r.run_id != r.trace_id


class TestPromptInput:
    def test_minimal(self):
        p = PromptInput(prompt="fix the bug")
        assert p.assistant == "codex"

    def test_full(self):
        p = PromptInput(prompt="add auth", repository="org/repo", assistant="claude-code")
        assert p.repository == "org/repo"
