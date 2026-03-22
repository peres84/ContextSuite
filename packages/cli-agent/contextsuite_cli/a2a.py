"""A2A helpers for the CLI Agent."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from contextsuite_shared.a2a import (
    A2A_TASK_NOT_FOUND,
    Artifact,
    DataPart,
    JSONRPCError,
    JSONRPCErrorResponse,
    JSONRPCSuccessResponse,
    Message,
    Role,
    Task,
    TaskError,
    TaskPayload,
    TaskResult,
    TaskState,
    TaskStatus,
    artifact_from_text,
    extract_data,
    extract_text,
    message_from_text,
)
from contextsuite_shared.agent_card import CLI_AGENT_ID, build_cli_agent_card


def build_agent_card(base_url: str):
    """Build the A2A agent card for the current base URL."""
    return build_cli_agent_card(base_url)


def ensure_assistant_id(assistant_id: str) -> None:
    """Validate the requested assistant id."""
    if assistant_id != CLI_AGENT_ID:
        raise LookupError(f"Unknown assistant_id: {assistant_id}")


def jsonrpc_success(request_id: str | int | None, result: Any) -> dict:
    """Create a JSON-RPC success response."""
    return JSONRPCSuccessResponse(id=request_id, result=result).model_dump(
        by_alias=True,
        exclude_none=True,
    )


def jsonrpc_error(
    request_id: str | int | None,
    *,
    code: int,
    message: str,
    data: Any | None = None,
) -> dict:
    """Create a JSON-RPC error response."""
    return JSONRPCErrorResponse(
        id=request_id,
        error=JSONRPCError(code=code, message=message, data=data),
    ).model_dump(by_alias=True, exclude_none=True)


def extract_task_payload(message: Message, metadata: dict[str, Any] | None = None) -> TaskPayload:
    """Convert an inbound A2A message into the internal TaskPayload model."""
    merged: dict[str, Any] = {}
    for payload in extract_data(message):
        task_payload = payload.get("taskPayload")
        candidate = task_payload if isinstance(task_payload, dict) else payload
        if isinstance(candidate.get("payload"), dict):
            merged.update(candidate["payload"])
        else:
            merged.update(candidate)

    metadata = metadata or {}
    message_metadata = message.metadata or {}

    if "prompt" not in merged:
        prompt = extract_text(message)
        if prompt:
            merged["prompt"] = prompt

    merged.setdefault(
        "assistant",
        metadata.get("assistant") or message_metadata.get("assistant") or "codex",
    )
    if "repository" not in merged:
        repository = metadata.get("repository") or message_metadata.get("repository")
        if repository:
            merged["repository"] = repository

    return TaskPayload.model_validate(merged)


def build_task_from_execution(
    *,
    task_id: str,
    context_id: str,
    inbound_message: Message,
    result: TaskResult | TaskError,
) -> Task:
    """Wrap the internal execution result in an A2A task object."""
    if isinstance(result, TaskError):
        summary = result.message
        state = TaskState.FAILED
        metadata = {
            "runId": result.run_id,
            "traceId": result.trace_id,
            "errorCode": str(result.error_code),
            "errorReason": result.reason,
        }
        artifacts: list[Artifact] = []
    else:
        summary = result.summary or "Task completed."
        state = result.state
        metadata = {
            "runId": result.run_id,
            "traceId": result.trace_id,
            "durationSeconds": result.duration_seconds,
        }
        artifacts = [Artifact.model_validate(item) for item in result.artifacts]
        if result.output:
            artifacts.append(
                artifact_from_text(
                    result.output,
                    name="execution-output",
                    description=summary,
                )
            )

    status_message = message_from_text(
        summary,
        role=Role.AGENT,
        task_id=task_id,
        context_id=context_id,
        metadata=metadata,
    )
    history = [
        inbound_message.model_copy(update={"task_id": task_id, "context_id": context_id}),
        status_message,
    ]
    return Task(
        id=task_id,
        contextId=context_id,
        status=TaskStatus(state=state, message=status_message),
        history=history,
        artifacts=artifacts,
        metadata=metadata,
    )


def submitted_task(message: Message) -> Task:
    """Build an initial submitted task snapshot."""
    task_id = message.task_id or uuid4().hex
    context_id = message.context_id or uuid4().hex
    status_message = message_from_text(
        "Task accepted by the CLI Agent.",
        role=Role.AGENT,
        task_id=task_id,
        context_id=context_id,
    )
    return Task(
        id=task_id,
        contextId=context_id,
        status=TaskStatus(state=TaskState.SUBMITTED, message=status_message),
        history=[
            message.model_copy(update={"task_id": task_id, "context_id": context_id}),
            status_message,
        ],
        artifacts=[],
        metadata={},
    )


def working_task(task: Task) -> Task:
    """Update a task snapshot to working."""
    status_message = message_from_text(
        "CLI task is running.",
        role=Role.AGENT,
        task_id=task.id,
        context_id=task.context_id,
    )
    return task.model_copy(
        update={
            "status": TaskStatus(state=TaskState.WORKING, message=status_message),
            "history": [task.history[0], status_message],
        }
    )


def task_not_found_error(request_id: str | int | None, task_id: str) -> dict:
    """Build a standard JSON-RPC error for missing tasks."""
    return jsonrpc_error(
        request_id,
        code=A2A_TASK_NOT_FOUND,
        message=f"Task {task_id} was not found.",
    )


def build_legacy_payload_message(task_id: str, payload: TaskPayload) -> Message:
    """Create a synthetic A2A message from the legacy /tasks/receive payload."""
    return Message(
        role=Role.USER,
        parts=[
            DataPart(data=payload.model_dump()),
            *message_from_text(payload.prompt, role=Role.USER).parts,
        ],
        taskId=task_id,
        contextId=payload.run_id,
        metadata={"assistant": payload.assistant, "repository": payload.repository},
    )


__all__ = [
    "build_agent_card",
    "build_legacy_payload_message",
    "build_task_from_execution",
    "ensure_assistant_id",
    "extract_task_payload",
    "jsonrpc_error",
    "jsonrpc_success",
    "submitted_task",
    "task_not_found_error",
    "working_task",
]
