"""Claude Code CLI adapter that runs Claude Code in a subprocess."""

from __future__ import annotations

import logging

from contextsuite_shared.a2a import TaskPayload, TaskResult
from contextsuite_shared.a2a.task import Artifact, TaskState

from contextsuite_cli.adapters.base import BaseAdapter
from contextsuite_cli.config import settings

logger = logging.getLogger(__name__)


class ClaudeCodeAdapter(BaseAdapter):
    """Adapter for the Claude Code CLI."""

    name = "claude"

    async def execute(self, payload: TaskPayload) -> TaskResult:
        """Run a prompt through the Claude Code CLI."""
        workspace = payload.workspace_path or settings.default_workspace
        workspace = self.prepare_workspace(workspace)
        full_prompt = self.build_prompt(payload)

        cmd = [
            "claude",
            "--print",
            "--dangerously-skip-permissions",
            full_prompt,
        ]

        logger.info("claude-code: running in %s (run=%s)", workspace, payload.run_id)

        try:
            proc = await self.run_subprocess(
                cmd,
                workspace,
                logger=logger,
                label=f"claude-code: run={payload.run_id}",
            )

            stdout_text = proc.stdout.decode("utf-8", errors="replace")
            stderr_text = proc.stderr.decode("utf-8", errors="replace")

            if proc.returncode == 0:
                logger.info("claude-code: completed (run=%s)", payload.run_id)
                return TaskResult(
                    task_id="",
                    state=TaskState.COMPLETED,
                    summary=f"Claude Code completed in {workspace}",
                    output=stdout_text,
                    artifacts=[
                        Artifact(
                            name="stdout",
                            parts=[],
                            metadata={"content": stdout_text[:5000]},
                        ),
                    ],
                )

            logger.warning(
                "claude-code: exited with code %d (run=%s)",
                proc.returncode,
                payload.run_id,
            )
            return TaskResult(
                task_id="",
                state=TaskState.FAILED,
                summary=f"Claude Code exited with code {proc.returncode}",
                output=stderr_text or stdout_text,
            )

        except FileNotFoundError:
            logger.error("claude-code: CLI not found")
            return TaskResult(
                task_id="",
                state=TaskState.FAILED,
                summary="Claude Code CLI not found. Install with: "
                "npm install -g @anthropic-ai/claude-code",
                output="",
            )
