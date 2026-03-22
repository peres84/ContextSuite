"""Base adapter interface and subprocess helpers for coding assistant CLIs."""

from __future__ import annotations

import asyncio
import os
import subprocess
from abc import ABC, abstractmethod

from contextsuite_shared.a2a import TaskPayload, TaskResult


class BaseAdapter(ABC):
    """Base class for coding assistant adapters."""

    name: str

    @staticmethod
    def build_prompt(payload: TaskPayload) -> str:
        """Build the prompt sent to the coding assistant."""
        sections = [payload.prompt]
        if payload.plan:
            sections.append(f"Plan:\n{payload.plan}")
        return "\n\n".join(section for section in sections if section)

    @staticmethod
    def prepare_workspace(workspace: str) -> str:
        """Normalize the target workspace path."""
        return os.path.expanduser(workspace)

    @staticmethod
    def _run_command(cmd: list[str], workspace: str) -> subprocess.CompletedProcess[bytes]:
        """Run a CLI command in a blocking subprocess."""
        return subprocess.run(
            cmd,
            capture_output=True,
            cwd=workspace,
            check=False,
        )

    async def run_subprocess(
        self,
        cmd: list[str],
        workspace: str,
    ) -> subprocess.CompletedProcess[bytes]:
        """Run a subprocess in a worker thread for Windows compatibility."""
        return await asyncio.to_thread(self._run_command, cmd, workspace)

    @abstractmethod
    async def execute(self, payload: TaskPayload) -> TaskResult:
        """Execute a task using the coding assistant CLI."""
        ...
