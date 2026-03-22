"""Task execution lifecycle — manages state transitions and adapter dispatch."""

from __future__ import annotations

import asyncio
import logging
import time

from contextsuite_shared.a2a import TaskPayload, TaskResult
from contextsuite_shared.a2a.error import ErrorCode, TaskError

from contextsuite_cli.adapters.base import BaseAdapter

logger = logging.getLogger(__name__)

# Default timeout for task execution (seconds)
DEFAULT_TIMEOUT = 300


async def execute_task(
    task_id: str,
    payload: TaskPayload,
    adapter: BaseAdapter,
    timeout: float = DEFAULT_TIMEOUT,
) -> TaskResult | TaskError:
    """Execute a task through an adapter with timeout and error handling.

    Returns TaskResult on success, TaskError on failure.
    """
    start = time.monotonic()
    logger.info(
        "execute_task: starting task=%s adapter=%s run=%s",
        task_id,
        adapter.name,
        payload.run_id,
    )

    try:
        result = await asyncio.wait_for(
            adapter.execute(payload),
            timeout=timeout,
        )
        duration = time.monotonic() - start

        # Ensure result has the right IDs
        result.task_id = task_id
        result.run_id = payload.run_id
        result.trace_id = payload.trace_id
        result.duration_seconds = duration

        logger.info(
            "execute_task: completed task=%s in %.1fs state=%s",
            task_id,
            duration,
            result.state,
        )
        return result

    except TimeoutError:
        duration = time.monotonic() - start
        logger.warning("execute_task: timeout after %.1fs task=%s", duration, task_id)
        return TaskError(
            task_id=task_id,
            error_code=ErrorCode.TIMEOUT,
            message=f"Task timed out after {timeout:.0f}s",
            run_id=payload.run_id,
            trace_id=payload.trace_id,
        )

    except Exception as exc:
        duration = time.monotonic() - start
        logger.exception("execute_task: failed task=%s after %.1fs", task_id, duration)
        return TaskError(
            task_id=task_id,
            error_code=ErrorCode.EXECUTION_FAILED,
            message=str(exc),
            reason=type(exc).__name__,
            run_id=payload.run_id,
            trace_id=payload.trace_id,
        )
