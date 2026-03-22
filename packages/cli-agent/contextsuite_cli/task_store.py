"""In-memory task store for A2A task polling."""

from __future__ import annotations

from threading import Lock

from contextsuite_shared.a2a import Task

_TASKS: dict[str, Task] = {}
_LOCK = Lock()


def save_task(task: Task) -> Task:
    """Persist the latest task snapshot in memory."""
    with _LOCK:
        _TASKS[task.id] = task
    return task


def get_task(task_id: str) -> Task | None:
    """Look up a task snapshot from memory."""
    with _LOCK:
        return _TASKS.get(task_id)
