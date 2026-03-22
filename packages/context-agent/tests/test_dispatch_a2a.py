"""Tests for the Context Agent A2A dispatch adapter."""

import sys
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[2] / "cli-agent"))

from contextsuite_agent.workflow.nodes.dispatch import dispatch_payload
from contextsuite_cli.server import app as cli_app
from contextsuite_shared.a2a import TaskPayload, TaskResult, TaskState


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
        duration_seconds=0.9,
    )


class _WrappedResponse:
    def __init__(self, response):
        self._response = response
        self.status_code = response.status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "request failed",
                request=httpx.Request("POST", self._response.request.url),
                response=httpx.Response(self.status_code),
            )

    def json(self):
        return self._response.json()


def test_dispatch_payload_prefers_a2a(monkeypatch):
    monkeypatch.setattr("contextsuite_cli.adapters.get_adapter", lambda name: DummyAdapter())
    monkeypatch.setattr("contextsuite_cli.executor.execute_task", _fake_execute_task)
    monkeypatch.setattr(
        "contextsuite_agent.workflow.nodes.dispatch.RunsRepo.update_run_status",
        lambda *args, **kwargs: {},
    )
    monkeypatch.setattr(
        "contextsuite_agent.workflow.nodes.dispatch.RunsRepo.save_outcome",
        lambda *args, **kwargs: {},
    )

    client = TestClient(cli_app)

    def fake_post(url, json, timeout):
        path = url.split("://", 1)[-1].split("/", 1)[-1]
        response = client.post("/" + path, json=json)
        return _WrappedResponse(response)

    monkeypatch.setattr("contextsuite_agent.workflow.nodes.dispatch.httpx.post", fake_post)

    payload = TaskPayload(
        run_id="run-1",
        trace_id="trace-1",
        prompt="Fix the bug",
        assistant="codex",
    )

    result = dispatch_payload(run_id="run-1", task_id="cli-task-1", payload=payload)

    assert result["dispatch_status"] == "completed"
    assert result["dispatch_result"]["summary"] == "CLI task completed"
    assert result["dispatch_result"]["output"] == "patched files"
