"""Regression tests for the Claude Code CLI adapter."""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from contextsuite_cli.adapters.claude_code import ClaudeCodeAdapter
from contextsuite_shared.a2a import TaskPayload, TaskState


class DummyProcess:
    def __init__(self, *, returncode: int, stdout: bytes = b"", stderr: bytes = b""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_claude_adapter_uses_positional_prompt(monkeypatch, tmp_path):
    captured: dict[str, object] = {}

    async def fake_run_subprocess(self, cmd, workspace, **_kwargs):
        captured["cmd"] = cmd
        captured["cwd"] = workspace
        return DummyProcess(returncode=0, stdout=b"OK\n")

    monkeypatch.setattr(ClaudeCodeAdapter, "run_subprocess", fake_run_subprocess)

    payload = TaskPayload(
        run_id="run-claude-1",
        trace_id="trace-claude-1",
        prompt="Update the page styling.",
        plan="Keep the primary green brand color.",
        assistant="claude",
        workspace_path=str(tmp_path),
    )

    result = asyncio.run(ClaudeCodeAdapter().execute(payload))

    assert captured["cmd"][:3] == [
        "claude",
        "--print",
        "--dangerously-skip-permissions",
    ]
    assert "--prompt" not in captured["cmd"]
    expected_prompt = (
        "Update the page styling.\n\nPlan:\nKeep the primary green brand color."
    )
    assert captured["cmd"][-1] == expected_prompt
    assert captured["cwd"] == str(tmp_path)
    assert result.state == TaskState.COMPLETED
    assert result.output == "OK\n"


def test_claude_adapter_surfaces_stderr_on_failure(monkeypatch, tmp_path):
    async def fake_run_subprocess(self, _cmd, _workspace, **_kwargs):
        return DummyProcess(returncode=2, stderr=b"error: execution failed")

    monkeypatch.setattr(ClaudeCodeAdapter, "run_subprocess", fake_run_subprocess)

    payload = TaskPayload(
        run_id="run-claude-2",
        trace_id="trace-claude-2",
        prompt="Update the page styling.",
        assistant="claude",
        workspace_path=str(tmp_path),
    )

    result = asyncio.run(ClaudeCodeAdapter().execute(payload))

    assert result.state == TaskState.FAILED
    assert result.summary == "Claude Code exited with code 2"
    assert result.output == "error: execution failed"
