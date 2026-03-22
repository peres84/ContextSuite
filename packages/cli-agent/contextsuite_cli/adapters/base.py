"""Base adapter interface and subprocess helpers for coding assistant CLIs."""

from __future__ import annotations

import asyncio
import os
import subprocess
import time
from abc import ABC, abstractmethod
from logging import Logger

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

    async def run_subprocess(
        self,
        cmd: list[str],
        workspace: str,
        *,
        logger: Logger | None = None,
        label: str = "subprocess",
        heartbeat_seconds: float = 10.0,
    ) -> subprocess.CompletedProcess[bytes]:
        """Run a subprocess and emit periodic heartbeat logs while it is alive."""
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=workspace,
        )

        start = time.monotonic()
        last_heartbeat = start

        while True:
            if proc.poll() is not None:
                break

            now = time.monotonic()
            if logger and (now - last_heartbeat) >= heartbeat_seconds:
                logger.info("%s still running after %.0fs", label, now - start)
                last_heartbeat = now
            await asyncio.sleep(1)

        stdout, stderr = proc.communicate()
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=proc.returncode,
            stdout=stdout,
            stderr=stderr,
        )

    @abstractmethod
    async def execute(self, payload: TaskPayload) -> TaskResult:
        """Execute a task using the coding assistant CLI."""
        ...
