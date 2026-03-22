"""Tests for the CLI Agent A2A server surface."""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from contextsuite_cli.server import app
from contextsuite_shared.a2a import TaskResult, TaskState


class DummyAdapter:
    name = "codex"


async def _fake_execute_task(task_id, payload, adapter):
    return TaskResult(
        task_id=task_id,
        state=TaskState.COMPLETED,
        summary="CLI task completed",
        output="patched files",
        run_id=payload.run_id,
        trace_id=payload.trace_id,
        duration_seconds=1.2,
    )


def test_message_send_executes_and_exposes_tasks_get(monkeypatch):
    monkeypatch.setattr("contextsuite_cli.adapters.get_adapter", lambda name: DummyAdapter())
    monkeypatch.setattr("contextsuite_cli.executor.execute_task", _fake_execute_task)

    client = TestClient(app)
    response = client.post(
        "/a2a/contextsuite-cli-agent",
        json={
            "jsonrpc": "2.0",
            "id": "1",
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "messageId": "msg-1",
                    "taskId": "cli-task-1",
                    "contextId": "run-1",
                    "parts": [
                        {"kind": "text", "text": "Fix the bug"},
                        {
                            "kind": "data",
                            "data": {
                                "taskPayload": {
                                    "run_id": "run-1",
                                    "trace_id": "trace-1",
                                    "prompt": "Fix the bug",
                                    "assistant": "codex",
                                }
                            },
                        },
                    ],
                }
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"]["id"] == "cli-task-1"
    assert body["result"]["status"]["state"] == "completed"

    poll = client.post(
        "/a2a/contextsuite-cli-agent",
        json={
            "jsonrpc": "2.0",
            "id": "2",
            "method": "tasks/get",
            "params": {"id": "cli-task-1"},
        },
    )

    assert poll.status_code == 200
    polled = poll.json()
    assert polled["result"]["id"] == "cli-task-1"
    assert polled["result"]["status"]["state"] == "completed"


def test_legacy_receive_still_works(monkeypatch):
    monkeypatch.setattr("contextsuite_cli.adapters.get_adapter", lambda name: DummyAdapter())
    monkeypatch.setattr("contextsuite_cli.executor.execute_task", _fake_execute_task)

    client = TestClient(app)
    response = client.post(
        "/tasks/receive",
        json={
            "task_id": "legacy-task-1",
            "payload": {
                "run_id": "run-legacy",
                "trace_id": "trace-legacy",
                "prompt": "Fix legacy path",
                "assistant": "codex",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["task_id"] == "legacy-task-1"
    assert body["state"] == "completed"
