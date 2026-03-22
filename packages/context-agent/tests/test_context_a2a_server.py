"""Tests for the Context Agent A2A server surface."""

from contextsuite_agent.server import app
from contextsuite_shared.types import ApprovalDecision, ApprovalStatus, RiskAssessment
from fastapi.testclient import TestClient


def _completed_result() -> dict:
    return {
        "run_id": "run-1",
        "trace_id": "trace-1",
        "assistant": "codex",
        "plan": "1. Fix the bug",
        "context_summary": "Incident about webhook null emails",
        "risk": RiskAssessment(),
        "approval": ApprovalDecision(
            approved=True,
            status=ApprovalStatus.APPROVED,
            reason="Auto-approved",
        ),
        "dispatch_status": "completed",
        "dispatch_result": {
            "state": "completed",
            "summary": "Executed successfully",
            "output": "done",
            "artifacts": [],
        },
        "saved_memory": None,
        "task_id": "cli-task-1",
    }


def test_agent_card_discovery():
    client = TestClient(app)

    response = client.get("/.well-known/agent-card.json?assistant_id=contextsuite-context-agent")

    assert response.status_code == 200
    body = response.json()
    assert body["protocolVersion"] == "0.3.0"
    assert body["url"].endswith("/a2a/contextsuite-context-agent")
    assert body["preferredTransport"] == "JSONRPC"


def test_message_send_returns_a2a_task(monkeypatch):
    from contextsuite_agent.workflow import workflow

    monkeypatch.setattr(workflow, "invoke", lambda payload: _completed_result() | payload)
    client = TestClient(app)

    response = client.post(
        "/a2a/contextsuite-context-agent",
        json={
            "jsonrpc": "2.0",
            "id": "1",
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": "Fix the webhook bug"}],
                    "messageId": "msg-1",
                }
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["jsonrpc"] == "2.0"
    assert body["id"] == "1"
    assert body["result"]["kind"] == "task"
    assert body["result"]["id"] == "run-1"
    assert body["result"]["contextId"] == "trace-1"
    assert body["result"]["status"]["state"] == "completed"
    assert body["result"]["metadata"]["cliTaskId"] == "cli-task-1"


def test_tasks_get_reconstructs_pending_approval(monkeypatch):
    monkeypatch.setattr(
        "contextsuite_agent.a2a.RunsRepo.get_run",
        lambda run_id: {
            "id": run_id,
            "trace_id": "trace-2",
            "assistant": "codex",
            "status": "reviewing",
        },
    )
    monkeypatch.setattr(
        "contextsuite_agent.a2a.PromptsRepo.get_prompt_for_run",
        lambda run_id: {"content": "Delete prod data"},
    )
    monkeypatch.setattr(
        "contextsuite_agent.a2a.ApprovalsRepo.get_approval_for_run",
        lambda run_id: {
            "decision": "escalated",
            "reason": "Requires human approval: high risk task",
        },
    )
    monkeypatch.setattr(
        "contextsuite_agent.a2a.RunsRepo.get_latest_outcome",
        lambda run_id: None,
    )

    client = TestClient(app)
    response = client.post(
        "/a2a/contextsuite-context-agent",
        json={
            "jsonrpc": "2.0",
            "id": "2",
            "method": "tasks/get",
            "params": {"id": "run-2", "historyLength": 2},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["id"] == "run-2"
    assert body["result"]["status"]["state"] == "input-required"
    assert any(
        part.get("kind") == "data" and part["data"]["approvalRequired"] is True
        for part in body["result"]["status"]["message"]["parts"]
    )


def test_message_send_resumes_escalated_task(monkeypatch):
    resumed = {}

    monkeypatch.setattr(
        "contextsuite_agent.persistence.runs.RunsRepo.get_run",
        lambda run_id: {"id": run_id},
    )
    monkeypatch.setattr(
        "contextsuite_agent.server.can_resume_task",
        lambda run_id: True,
    )

    def fake_resume(**kwargs):
        resumed.update(kwargs)
        return _completed_result()

    monkeypatch.setattr("contextsuite_agent.workflow.resume.resolve_human_approval", fake_resume)

    client = TestClient(app)
    response = client.post(
        "/a2a/contextsuite-context-agent",
        json={
            "jsonrpc": "2.0",
            "id": "3",
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "messageId": "msg-approval",
                    "taskId": "run-1",
                    "contextId": "trace-1",
                    "parts": [
                        {
                            "kind": "data",
                            "data": {
                                "approval": {
                                    "approved": True,
                                    "reviewer": "human-cli",
                                }
                            },
                        }
                    ],
                }
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["status"]["state"] == "completed"
    assert resumed["run_id"] == "run-1"
    assert resumed["approved"] is True
