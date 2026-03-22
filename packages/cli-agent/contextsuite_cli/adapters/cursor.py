"""Cursor CLI adapter that runs Cursor in a subprocess."""

from __future__ import annotations

import logging

from contextsuite_shared.a2a import TaskPayload, TaskResult
from contextsuite_shared.a2a.task import Artifact, TaskState

from contextsuite_cli.adapters.base import BaseAdapter
from contextsuite_cli.config import settings

logger = logging.getLogger(__name__)


class CursorAdapter(BaseAdapter):
    """Adapter for the Cursor CLI (cursor-agent)."""

    name = "cursor"

    async def execute(self, payload: TaskPayload) -> TaskResult:
        """Run a prompt through the Cursor CLI."""
        workspace = payload.workspace_path or settings.default_workspace
        workspace = self.prepare_workspace(workspace)
        full_prompt = self.build_prompt(payload)

        cmd = [
            "cursor",
            "--prompt",
            full_prompt,
        ]

        logger.info("cursor: running in %s (run=%s)", workspace, payload.run_id)

        try:
            proc = await self.run_subprocess(cmd, workspace)

            stdout_text = proc.stdout.decode("utf-8", errors="replace")
            stderr_text = proc.stderr.decode("utf-8", errors="replace")

            if proc.returncode == 0:
                logger.info("cursor: completed (run=%s)", payload.run_id)
                return TaskResult(
                    task_id="",
                    state=TaskState.COMPLETED,
                    summary=f"Cursor completed in {workspace}",
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
                "cursor: exited with code %d (run=%s)",
                proc.returncode,
                payload.run_id,
            )
            return TaskResult(
                task_id="",
                state=TaskState.FAILED,
                summary=f"Cursor exited with code {proc.returncode}",
                output=stderr_text or stdout_text,
            )

        except FileNotFoundError:
            logger.error("cursor: CLI not found")
            return TaskResult(
                task_id="",
                state=TaskState.FAILED,
                summary="Cursor CLI not found.",
                output="",
            )
