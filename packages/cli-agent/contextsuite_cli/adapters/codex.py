"""Codex CLI adapter that runs the current Codex exec command."""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path

from contextsuite_shared.a2a import TaskPayload, TaskResult
from contextsuite_shared.a2a.task import Artifact, TaskState

from contextsuite_cli.adapters.base import BaseAdapter
from contextsuite_cli.config import settings

logger = logging.getLogger(__name__)


class CodexAdapter(BaseAdapter):
    """Adapter for the OpenAI Codex CLI."""

    name = "codex"

    async def execute(self, payload: TaskPayload) -> TaskResult:
        """Run a prompt through the Codex CLI."""
        workspace = payload.workspace_path or settings.default_workspace
        workspace = self.prepare_workspace(workspace)
        full_prompt = self.build_prompt(payload)

        output_fd, output_path = tempfile.mkstemp(
            prefix="contextsuite-codex-",
            suffix=".txt",
        )
        os.close(output_fd)

        cmd = [
            "codex",
            "exec",
            "--skip-git-repo-check",
            "--full-auto",
            "--output-last-message",
            output_path,
            full_prompt,
        ]

        logger.info(
            "codex: running in %s (run=%s)",
            workspace,
            payload.run_id,
        )

        try:
            proc = await self.run_subprocess(cmd, workspace)

            stdout_text = proc.stdout.decode("utf-8", errors="replace")
            stderr_text = proc.stderr.decode("utf-8", errors="replace")
            output_text = Path(output_path).read_text(encoding="utf-8").strip()
            content = output_text or stderr_text or stdout_text

            if proc.returncode == 0:
                logger.info("codex: completed successfully (run=%s)", payload.run_id)
                return TaskResult(
                    task_id="",  # filled by lifecycle
                    state=TaskState.COMPLETED,
                    summary=f"Codex completed successfully in {workspace}",
                    output=content,
                    artifacts=[
                        Artifact(
                            name="codex-output",
                            parts=[],
                            metadata={"content": content[:5000]},
                        ),
                    ],
                )

            logger.warning(
                "codex: exited with code %d (run=%s)",
                proc.returncode,
                payload.run_id,
            )
            return TaskResult(
                task_id="",
                state=TaskState.FAILED,
                summary=f"Codex exited with code {proc.returncode}",
                output=content,
                artifacts=[
                    Artifact(
                        name="stderr",
                        parts=[],
                        metadata={"content": content[:5000]},
                    ),
                ],
            )

        except FileNotFoundError:
            logger.error("codex: CLI not found - is it installed?")
            return TaskResult(
                task_id="",
                state=TaskState.FAILED,
                summary="Codex CLI not found. Install with: npm install -g @openai/codex",
                output="",
            )
        finally:
            try:
                os.remove(output_path)
            except FileNotFoundError:
                pass
