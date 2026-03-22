"""Regression tests for the Codex CLI adapter."""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from contextsuite_cli.adapters.codex import CodexAdapter
from contextsuite_shared.a2a import TaskPayload, TaskState


class DummyProcess:
    def __init__(self, *, returncode: int, stdout: bytes = b"", stderr: bytes = b""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_codex_adapter_uses_exec_and_reads_last_message(monkeypatch, tmp_path):
    captured: dict[str, object] = {}

    async def fake_run_subprocess(self, cmd, workspace):
        captured["cmd"] = cmd
        captured["cwd"] = workspace
        output_path = Path(cmd[cmd.index("--output-last-message") + 1])
        output_path.write_text("Applied the requested update.", encoding="utf-8")
        return DummyProcess(returncode=0, stdout=b'{"type":"turn.completed"}\n')

    monkeypatch.setattr(CodexAdapter, "run_subprocess", fake_run_subprocess)

    payload = TaskPayload(
        run_id="run-1",
        trace_id="trace-1",
        prompt="Update the page styling.",
        plan="Keep the primary green brand color.",
        assistant="codex",
        workspace_path=str(tmp_path),
    )

    result = asyncio.run(CodexAdapter().execute(payload))

    assert tuple(captured["cmd"][:2]) == ("codex", "exec")
    assert "--full-auto" in captured["cmd"]
    assert "--skip-git-repo-check" in captured["cmd"]
    assert captured["cwd"] == str(tmp_path)
    assert result.state == TaskState.COMPLETED
    assert result.output == "Applied the requested update."
    assert "completed successfully" in (result.summary or "").lower()


def test_codex_adapter_surfaces_stderr_on_failure(monkeypatch, tmp_path):
    async def fake_run_subprocess(self, _cmd, _workspace):
        return DummyProcess(returncode=2, stderr=b"error: execution failed")

    monkeypatch.setattr(CodexAdapter, "run_subprocess", fake_run_subprocess)

    payload = TaskPayload(
        run_id="run-2",
        trace_id="trace-2",
        prompt="Update the page styling.",
        assistant="codex",
        workspace_path=str(tmp_path),
    )

    result = asyncio.run(CodexAdapter().execute(payload))

    assert result.state == TaskState.FAILED
    assert result.summary == "Codex exited with code 2"
    assert result.output == "error: execution failed"
