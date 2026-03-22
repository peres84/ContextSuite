"""Tests for A2A contract schemas and shared types."""

import json

import pytest
from contextsuite_shared.a2a import (
    Artifact,
    DataPart,
    ErrorCode,
    FilePart,
    JSONRPCRequest,
    Message,
    MessageSendConfiguration,
    MessageSendParams,
    Role,
    Task,
    TaskError,
    TaskPayload,
    TaskQueryParams,
    TaskResult,
    TaskState,
    TaskStatus,
    TaskStatusUpdate,
    TextPart,
)
from contextsuite_shared.agent_card import (
    CLI_AGENT_ID,
    CONTEXT_AGENT_ID,
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


class TestTaskState:
    def test_all_states_exist(self):
        expected = {
            "submitted",
            "working",
            "input-required",
            "completed",
            "canceled",
            "failed",
            "rejected",
            "auth-required",
            "unknown",
        }
        assert {s.value for s in TaskState} == expected


class TestTask:
    def test_minimal_task(self):
        task = Task(id="t-1", context_id="ctx-1", status=TaskStatus(state=TaskState.WORKING))
        assert task.id == "t-1"
        assert task.context_id == "ctx-1"
        assert task.kind == "task"
        assert task.history == []
        assert task.artifacts == []

    def test_task_with_history(self):
        msg = Message(role=Role.USER, parts=[TextPart(text="fix the bug")])
        task = Task(
            id="t-2",
            context_id="ctx-2",
            status=TaskStatus(state=TaskState.WORKING),
            history=[msg],
        )
        assert len(task.history) == 1
        assert task.messages[0].parts[0].text == "fix the bug"

    def test_task_roundtrip_json(self):
        task = Task(
            id="t-3",
            context_id="ctx-3",
            status=TaskStatus(
                state=TaskState.COMPLETED,
                message=Message(role=Role.AGENT, parts=[TextPart(text="done")]),
            ),
            history=[Message(role=Role.USER, parts=[TextPart(text="fix it")])],
            artifacts=[Artifact(name="patch", parts=[TextPart(text="diff")])],
        )
        data = json.loads(task.model_dump_json(by_alias=True, exclude_none=True))
        assert data["kind"] == "task"
        assert data["contextId"] == "ctx-3"
        assert data["status"]["state"] == "completed"
        restored = Task.model_validate(data)
        assert restored.id == task.id
        assert restored.status.state == task.status.state

    def test_task_accepts_legacy_messages_field(self):
        task = Task.model_validate(
            {
                "id": "t-4",
                "contextId": "ctx-4",
                "status": {"state": "working"},
                "messages": [{"role": "user", "parts": [{"kind": "text", "text": "hello"}]}],
            }
        )
        assert len(task.history) == 1
        assert task.messages[0].parts[0].text == "hello"


class TestParts:
    def test_text_part(self):
        part = TextPart(text="hello")
        assert part.kind == "text"
        assert part.type == "text"

    def test_file_part(self):
        part = FilePart(
            file={
                "uri": "file:///tmp/a.py",
                "mimeType": "text/x-python",
                "name": "a.py",
            }
        )
        assert part.kind == "file"
        assert part.file.name == "a.py"

    def test_legacy_file_part(self):
        part = FilePart.model_validate(
            {
                "type": "file",
                "uri": "file:///tmp/a.py",
                "mediaType": "text/x-python",
                "name": "a.py",
            }
        )
        assert part.file.uri == "file:///tmp/a.py"
        assert part.file.mime_type == "text/x-python"

    def test_data_part(self):
        part = DataPart(data={"key": "value"})
        assert part.kind == "data"
        assert part.data["key"] == "value"


class TestTaskPayload:
    def test_minimal_payload(self):
        payload = TaskPayload(run_id="r1", trace_id="t1", prompt="fix the bug")
        assert payload.risk_level == RiskLevel.LOW
        assert payload.assistant == "codex"

    def test_full_payload(self):
        payload = TaskPayload(
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
        assert payload.risk_level == RiskLevel.HIGH
        assert payload.repository == "org/repo"


class TestTaskStatusUpdate:
    def test_status_update_event(self):
        status = TaskStatusUpdate(
            task_id="t-1",
            context_id="ctx-1",
            status=TaskStatus(state=TaskState.WORKING),
            final=False,
        )
        assert status.kind == "status-update"
        assert status.context_id == "ctx-1"


class TestTaskResult:
    def test_result(self):
        result = TaskResult(
            task_id="t-1",
            state=TaskState.COMPLETED,
            summary="Bug fixed",
            duration_seconds=12.5,
            run_id="r1",
        )
        assert result.state == TaskState.COMPLETED
        assert result.duration_seconds == 12.5


class TestTaskError:
    def test_error(self):
        error = TaskError(
            task_id="t-1",
            error_code=ErrorCode.POLICY_BLOCKED,
            message="Dangerous operation blocked",
            reason="Attempted to delete production database",
        )
        assert error.error_code == ErrorCode.POLICY_BLOCKED

    def test_all_error_codes(self):
        assert len(ErrorCode) == 8


class TestJSONRPC:
    def test_message_send_params(self):
        params = MessageSendParams(
            message=Message(role=Role.USER, parts=[TextPart(text="hello")]),
            configuration=MessageSendConfiguration(
                blocking=True,
                history_length=2,
                accepted_output_modes=["application/json"],
            ),
        )
        data = params.model_dump(by_alias=True, exclude_none=True)
        assert data["configuration"]["historyLength"] == 2
        assert data["configuration"]["acceptedOutputModes"] == ["application/json"]

    def test_request_roundtrip(self):
        request = JSONRPCRequest(
            id="1",
            method="tasks/get",
            params=TaskQueryParams(id="task-1", history_length=1).model_dump(
                by_alias=True,
                exclude_none=True,
            ),
        )
        payload = request.model_dump(exclude_none=True)
        assert payload["jsonrpc"] == "2.0"
        assert payload["method"] == "tasks/get"


class TestAgentCards:
    def test_context_agent_card(self):
        card = build_context_agent_card("http://localhost:8000")
        assert card.url == f"http://localhost:8000/a2a/{CONTEXT_AGENT_ID}"
        assert card.preferred_transport == "JSONRPC"
        assert card.capabilities.streaming is False
        assert len(card.skills) == 5

    def test_cli_agent_card(self):
        card = build_cli_agent_card("http://localhost:8001")
        assert card.url == f"http://localhost:8001/a2a/{CLI_AGENT_ID}"
        assert card.capabilities.streaming is False
        assert len(card.skills) == 3

    def test_agent_card_serialization(self):
        card = build_context_agent_card()
        data = json.loads(card.model_dump_json(by_alias=True, exclude_none=True))
        assert data["protocolVersion"] == "0.3.0"
        assert data["preferredTransport"] == "JSONRPC"
        assert data["url"].endswith(f"/a2a/{CONTEXT_AGENT_ID}")


class TestApproval:
    def test_auto_approval(self):
        approval = ApprovalDecision(approved=True)
        assert approval.reviewer == "auto"
        assert approval.risk.level == RiskLevel.LOW
        assert approval.status == ApprovalStatus.APPROVED

    def test_escalated_status(self):
        approval = ApprovalDecision(approved=False, status=ApprovalStatus.ESCALATED)
        assert approval.status == ApprovalStatus.ESCALATED
        assert not approval.approved

    def test_blocked_with_violations(self):
        approval = ApprovalDecision(
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
        assert not approval.approved
        assert len(approval.policy_violations) == 1
        assert approval.risk.signals[0].weight == 3.0
        assert approval.status == ApprovalStatus.REJECTED


class TestRiskLevel:
    def test_all_levels(self):
        assert set(RiskLevel) == {"low", "medium", "high"}


class TestRunMeta:
    def test_auto_generates_ids(self):
        run = RunMeta()
        assert len(run.run_id) == 32
        assert len(run.trace_id) == 32
        assert run.run_id != run.trace_id


class TestPromptInput:
    def test_minimal(self):
        prompt = PromptInput(prompt="fix the bug")
        assert prompt.assistant == "codex"

    def test_full(self):
        prompt = PromptInput(prompt="add auth", repository="org/repo", assistant="claude-code")
        assert prompt.repository == "org/repo"

    def test_status_update_requires_context_id(self):
        with pytest.raises(Exception):
            TaskStatusUpdate(task_id="t-1", status=TaskStatus(state=TaskState.WORKING))
