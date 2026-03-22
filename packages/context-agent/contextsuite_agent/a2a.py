"""A2A helpers for the Context Agent."""

from __future__ import annotations

from typing import Any

from contextsuite_shared.a2a import (
    A2A_TASK_NOT_FOUND,
    A2A_TASK_NOT_RESUMABLE,
    Artifact,
    DataPart,
    JSONRPCError,
    JSONRPCErrorResponse,
    JSONRPCSuccessResponse,
    Message,
    Role,
    Task,
    TaskState,
    TaskStatus,
    artifact_from_text,
    extract_data,
    extract_text,
    message_from_text,
)
from contextsuite_shared.agent_card import CONTEXT_AGENT_ID, build_context_agent_card

from contextsuite_agent.persistence import ApprovalsRepo, PromptsRepo, RunsRepo


def build_agent_card(base_url: str):
    """Build the A2A agent card for the current base URL."""
    return build_context_agent_card(base_url)


def ensure_assistant_id(assistant_id: str) -> None:
    """Validate the requested assistant id."""
    if assistant_id != CONTEXT_AGENT_ID:
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


def extract_submission(message: Message, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Extract a workflow submission from an inbound A2A message."""
    merged: dict[str, Any] = {}
    for payload in extract_data(message):
        if isinstance(payload.get("submission"), dict):
            merged.update(payload["submission"])
        else:
            merged.update(payload)

    message_metadata = message.metadata or {}
    metadata = metadata or {}

    prompt = (
        merged.get("prompt")
        or metadata.get("prompt")
        or message_metadata.get("prompt")
        or extract_text(message)
    )
    repository = (
        merged.get("repository") or metadata.get("repository") or message_metadata.get("repository")
    )
    assistant = (
        merged.get("assistant")
        or metadata.get("assistant")
        or message_metadata.get("assistant")
        or "codex"
    )

    if not prompt:
        raise ValueError("No prompt found in A2A message.")

    return {
        "prompt": prompt,
        "repository": repository,
        "assistant": assistant,
    }


def extract_approval_response(message: Message) -> dict[str, Any] | None:
    """Extract an approval decision from an inbound A2A continuation message."""
    for payload in extract_data(message):
        approval = payload.get("approval")
        candidate = approval if isinstance(approval, dict) else payload
        if "approved" in candidate:
            return {
                "approved": bool(candidate.get("approved")),
                "reviewer": candidate.get("reviewer", "a2a-client"),
                "reason": candidate.get("reason"),
            }

    text = extract_text(message).strip().lower()
    if text in {"approve", "approved", "yes"}:
        return {"approved": True, "reviewer": "a2a-client", "reason": "Approved via A2A"}
    if text in {"reject", "rejected", "no"}:
        return {"approved": False, "reviewer": "a2a-client", "reason": "Rejected via A2A"}
    return None


def approval_requires_input(approval: dict[str, Any] | None) -> bool:
    """Check whether the latest approval record means the task is awaiting input."""
    return bool(approval and approval.get("decision") == "escalated")


def can_resume_task(run_id: str) -> bool:
    """Check if a run is currently awaiting human approval."""
    return approval_requires_input(ApprovalsRepo.get_approval_for_run(run_id))


def build_task_from_result(
    result: dict[str, Any],
    inbound_message: Message,
    *,
    history_length: int | None = None,
) -> Task:
    """Build an A2A task from the immediate workflow result."""
    run_id = str(result["run_id"])
    context_id = str(result["trace_id"])
    approval = result.get("approval")
    dispatch_result = result.get("dispatch_result") or {}
    dispatch_status = result.get("dispatch_status") or "working"

    state, status_message, artifacts = _build_runtime_state(
        run_id=run_id,
        context_id=context_id,
        approval=approval,
        dispatch_status=dispatch_status,
        dispatch_result=dispatch_result,
        cli_task_id=result.get("task_id"),
    )

    history = _trim_history(
        [
            inbound_message.model_copy(update={"task_id": run_id, "context_id": context_id}),
            status_message,
        ],
        history_length,
    )

    return Task(
        id=run_id,
        contextId=context_id,
        status=TaskStatus(state=state, message=status_message),
        history=history,
        artifacts=artifacts,
        metadata={
            "runId": run_id,
            "traceId": context_id,
            "assistant": result.get("assistant", "codex"),
            "approvalStatus": str(getattr(approval, "status", "")) if approval else None,
            "cliTaskId": result.get("task_id"),
            "savedMemory": result.get("saved_memory"),
        },
    )


def get_persisted_task(run_id: str, *, history_length: int | None = None) -> Task:
    """Reconstruct an A2A task from persisted run state."""
    run = RunsRepo.get_run(run_id)
    if not run:
        raise LookupError(run_id)

    prompt_record = PromptsRepo.get_prompt_for_run(run_id)
    approval = ApprovalsRepo.get_approval_for_run(run_id)
    outcome = RunsRepo.get_latest_outcome(run_id)

    context_id = str(run["trace_id"])
    prompt = prompt_record["content"] if prompt_record else ""

    state, status_message, artifacts = _build_persisted_state(
        run_id=run_id,
        context_id=context_id,
        run=run,
        approval=approval,
        outcome=outcome,
    )

    history = _trim_history(
        [
            Message(
                role=Role.USER,
                parts=[DataPart(data={"prompt": prompt})]
                if not prompt
                else message_from_text(
                    prompt,
                    role=Role.USER,
                    task_id=run_id,
                    context_id=context_id,
                ).parts,
                taskId=run_id,
                contextId=context_id,
                metadata={"source": "persistence"},
            ),
            status_message,
        ],
        history_length,
    )

    return Task(
        id=run_id,
        contextId=context_id,
        status=TaskStatus(state=state, message=status_message),
        history=history,
        artifacts=artifacts,
        metadata={
            "runId": run_id,
            "traceId": context_id,
            "assistant": run.get("assistant", "codex"),
            "approvalStatus": approval.get("decision") if approval else None,
            "cliTaskId": outcome.get("task_id") if outcome else None,
        },
    )


def terminal_task_error(run_id: str) -> dict:
    """Build a standard JSON-RPC error for non-resumable runs."""
    return jsonrpc_error(
        None,
        code=A2A_TASK_NOT_RESUMABLE,
        message=f"Task {run_id} is not awaiting additional input.",
    )


def task_not_found_error(request_id: str | int | None, task_id: str) -> dict:
    """Build a standard JSON-RPC error for missing tasks."""
    return jsonrpc_error(
        request_id,
        code=A2A_TASK_NOT_FOUND,
        message=f"Task {task_id} was not found.",
    )


def _build_runtime_state(
    *,
    run_id: str,
    context_id: str,
    approval: Any,
    dispatch_status: str,
    dispatch_result: dict[str, Any],
    cli_task_id: str | None,
) -> tuple[TaskState, Message, list[Artifact]]:
    approval_status = str(getattr(approval, "status", "")) if approval else ""
    approval_reason = getattr(approval, "reason", "") if approval else ""

    if approval_status == "escalated":
        status_message = Message(
            role=Role.AGENT,
            parts=[
                DataPart(
                    data={
                        "approvalRequired": True,
                        "approved": False,
                        "reason": approval_reason,
                        "resumeWith": {
                            "approved": True,
                            "reviewer": "human-cli",
                            "reason": "Reviewed and approved",
                        },
                    }
                ),
                *message_from_text(
                    approval_reason or "Human approval is required before execution can continue.",
                    role=Role.AGENT,
                    task_id=run_id,
                    context_id=context_id,
                ).parts,
            ],
            taskId=run_id,
            contextId=context_id,
            metadata={"approvalStatus": approval_status},
        )
        return TaskState.INPUT_REQUIRED, status_message, []

    if approval_status == "rejected":
        status_message = message_from_text(
            approval_reason or "The task was rejected by policy.",
            role=Role.AGENT,
            task_id=run_id,
            context_id=context_id,
            metadata={"approvalStatus": approval_status},
        )
        return TaskState.REJECTED, status_message, []

    dispatch_state = dispatch_result.get("state") or dispatch_status
    if dispatch_state == "completed":
        summary = dispatch_result.get("summary") or "Task completed successfully."
        status_message = message_from_text(
            summary,
            role=Role.AGENT,
            task_id=run_id,
            context_id=context_id,
            metadata={"cliTaskId": cli_task_id},
        )
        artifacts = _artifacts_from_dispatch_result(dispatch_result, summary)
        return TaskState.COMPLETED, status_message, artifacts

    if dispatch_state == "failed":
        summary = dispatch_result.get("summary") or dispatch_result.get("message") or "Task failed."
        status_message = message_from_text(
            summary,
            role=Role.AGENT,
            task_id=run_id,
            context_id=context_id,
            metadata={
                "cliTaskId": cli_task_id,
                "errorCode": dispatch_result.get("error_code"),
            },
        )
        artifacts = _artifacts_from_dispatch_result(dispatch_result, summary)
        return TaskState.FAILED, status_message, artifacts

    status_message = message_from_text(
        "Task accepted and is being processed.",
        role=Role.AGENT,
        task_id=run_id,
        context_id=context_id,
        metadata={"cliTaskId": cli_task_id},
    )
    return TaskState.WORKING, status_message, []


def _build_persisted_state(
    *,
    run_id: str,
    context_id: str,
    run: dict[str, Any],
    approval: dict[str, Any] | None,
    outcome: dict[str, Any] | None,
) -> tuple[TaskState, Message, list[Artifact]]:
    if outcome:
        if outcome.get("status") == "completed":
            summary = outcome.get("summary") or "Task completed successfully."
            return (
                TaskState.COMPLETED,
                message_from_text(
                    summary,
                    role=Role.AGENT,
                    task_id=run_id,
                    context_id=context_id,
                    metadata={"cliTaskId": outcome.get("task_id")},
                ),
                _artifacts_from_persisted_outcome(outcome, summary),
            )

        summary = outcome.get("summary") or outcome.get("error_message") or "Task failed."
        return (
            TaskState.FAILED,
            message_from_text(
                summary,
                role=Role.AGENT,
                task_id=run_id,
                context_id=context_id,
                metadata={
                    "cliTaskId": outcome.get("task_id"),
                    "errorCode": outcome.get("error_code"),
                },
            ),
            _artifacts_from_persisted_outcome(outcome, summary),
        )

    if approval_requires_input(approval):
        reason = (
            approval.get("reason") or "Human approval is required before execution can continue."
        )
        return (
            TaskState.INPUT_REQUIRED,
            Message(
                role=Role.AGENT,
                parts=[
                    DataPart(
                        data={
                            "approvalRequired": True,
                            "approved": False,
                            "reason": reason,
                            "resumeWith": {
                                "approved": True,
                                "reviewer": "human-cli",
                                "reason": "Reviewed and approved",
                            },
                        }
                    ),
                    *message_from_text(
                        reason,
                        role=Role.AGENT,
                        task_id=run_id,
                        context_id=context_id,
                    ).parts,
                ],
                taskId=run_id,
                contextId=context_id,
                metadata={"approvalStatus": approval.get("decision")},
            ),
            [],
        )

    if approval and approval.get("decision") == "rejected":
        reason = approval.get("reason") or "The task was rejected."
        return (
            TaskState.REJECTED,
            message_from_text(
                reason,
                role=Role.AGENT,
                task_id=run_id,
                context_id=context_id,
                metadata={"approvalStatus": approval.get("decision")},
            ),
            [],
        )

    run_status = run.get("status", "unknown")
    status_map = {
        "pending": TaskState.SUBMITTED,
        "retrieving": TaskState.WORKING,
        "planning": TaskState.WORKING,
        "reviewing": TaskState.WORKING,
        "approved": TaskState.WORKING,
        "dispatched": TaskState.WORKING,
        "working": TaskState.WORKING,
        "completed": TaskState.COMPLETED,
        "failed": TaskState.FAILED,
        "cancelled": TaskState.CANCELED,
        "rejected": TaskState.REJECTED,
    }
    state = status_map.get(run_status, TaskState.UNKNOWN)
    text = f"Run status: {run_status}"
    return (
        state,
        message_from_text(
            text,
            role=Role.AGENT,
            task_id=run_id,
            context_id=context_id,
        ),
        [],
    )


def _artifacts_from_dispatch_result(
    dispatch_result: dict[str, Any],
    summary: str,
) -> list[Artifact]:
    artifacts = [
        Artifact.model_validate(item) for item in dispatch_result.get("artifacts", []) or []
    ]
    output = dispatch_result.get("output")
    if output:
        artifacts.append(
            artifact_from_text(
                output,
                name="execution-output",
                description=summary,
            )
        )
    return artifacts


def _artifacts_from_persisted_outcome(outcome: dict[str, Any], summary: str) -> list[Artifact]:
    artifacts = [Artifact.model_validate(item) for item in outcome.get("artifacts", []) or []]
    output = outcome.get("output")
    if output:
        artifacts.append(
            artifact_from_text(
                output,
                name="execution-output",
                description=summary,
            )
        )
    return artifacts


def _trim_history(history: list[Message], history_length: int | None) -> list[Message]:
    if not history_length or history_length <= 0:
        return history
    return history[-history_length:]


__all__ = [
    "build_agent_card",
    "build_task_from_result",
    "can_resume_task",
    "ensure_assistant_id",
    "extract_approval_response",
    "extract_submission",
    "get_persisted_task",
    "jsonrpc_error",
    "jsonrpc_success",
    "task_not_found_error",
    "terminal_task_error",
]
