"""Base adapter interface for coding assistant CLIs."""

from abc import ABC, abstractmethod

from contextsuite_shared.a2a import TaskPayload, TaskResult


class BaseAdapter(ABC):
    """Base class for coding assistant adapters."""

    name: str

    @abstractmethod
    async def execute(self, payload: TaskPayload) -> TaskResult:
        """Execute a task using the coding assistant CLI."""
        ...
