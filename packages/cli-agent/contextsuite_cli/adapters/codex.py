"""Codex CLI adapter — runs OpenAI Codex CLI as a subprocess."""

from __future__ import annotations

import asyncio
import logging
import os

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
        workspace = os.path.expanduser(workspace)

        # Build the prompt with context
        full_prompt = payload.prompt
        if payload.plan:
            full_prompt = f"{payload.prompt}\n\nPlan:\n{payload.plan}"

        # Build codex command
        # codex --quiet --auto-edit --prompt "..."
        cmd = [
            "codex",
            "--quiet",
            "--auto-edit",
            "--prompt",
            full_prompt,
        ]

        logger.info(
            "codex: running in %s (run=%s)",
            workspace,
            payload.run_id,
        )

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workspace,
            )
            stdout, stderr = await proc.communicate()

            stdout_text = stdout.decode("utf-8", errors="replace")
            stderr_text = stderr.decode("utf-8", errors="replace")

            if proc.returncode == 0:
                logger.info("codex: completed successfully (run=%s)", payload.run_id)
                return TaskResult(
                    task_id="",  # filled by lifecycle
                    state=TaskState.COMPLETED,
                    summary=f"Codex completed successfully in {workspace}",
                    output=stdout_text,
                    artifacts=[
                        Artifact(
                            name="stdout",
                            parts=[],
                            metadata={"content": stdout_text[:5000]},
                        ),
                    ],
                )
            else:
                logger.warning(
                    "codex: exited with code %d (run=%s)",
                    proc.returncode,
                    payload.run_id,
                )
                return TaskResult(
                    task_id="",
                    state=TaskState.FAILED,
                    summary=f"Codex exited with code {proc.returncode}",
                    output=stderr_text or stdout_text,
                    artifacts=[
                        Artifact(
                            name="stderr",
                            parts=[],
                            metadata={"content": stderr_text[:5000]},
                        ),
                    ],
                )

        except FileNotFoundError:
            logger.error("codex: CLI not found — is it installed?")
            return TaskResult(
                task_id="",
                state=TaskState.FAILED,
                summary="Codex CLI not found. Install with: npm install -g @openai/codex",
                output="",
            )
