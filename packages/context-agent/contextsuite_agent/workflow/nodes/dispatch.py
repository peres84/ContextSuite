"""A2A dispatch node - sends the packaged task to the CLI Agent."""

from __future__ import annotations

import logging
from uuid import uuid4

import httpx
from contextsuite_shared.a2a import (
    DataPart,
    JSONRPCRequest,
    Message,
    MessageSendConfiguration,
    MessageSendParams,
    Role,
    Task,
    TextPart,
)
from contextsuite_shared.agent_card import CLI_AGENT_ID

from contextsuite_agent.config import settings
from contextsuite_agent.persistence import RunsRepo
from contextsuite_agent.workflow.state import AgentState

logger = logging.getLogger(__name__)


def dispatch_payload(*, run_id: str, task_id: str, payload) -> dict:
    """Dispatch a prepared A2A payload to the CLI Agent and persist the outcome."""
    a2a_url = f"http://{settings.cli_agent_host}:{settings.cli_agent_port}/a2a/{CLI_AGENT_ID}"
    legacy_url = f"http://{settings.cli_agent_host}:{settings.cli_agent_port}/tasks/receive"

    logger.info("dispatch: sending task=%s to %s (run=%s)", task_id, a2a_url, run_id)
    RunsRepo.update_run_status(run_id, "working")

    try:
        response = httpx.post(
            a2a_url,
            json=_build_a2a_request(task_id=task_id, payload=payload),
            timeout=330.0,
        )
        if response.status_code not in {404, 405}:
            response.raise_for_status()
            rpc_data = response.json()
            result_data = _convert_a2a_response(rpc_data)
            return _persist_dispatch_result(run_id=run_id, task_id=task_id, result_data=result_data)

        logger.warning("dispatch: A2A route unavailable, falling back to %s", legacy_url)
        response = httpx.post(
            legacy_url,
            json={"task_id": task_id, "payload": payload.model_dump()},
            timeout=330.0,
        )
        response.raise_for_status()
        result_data = response.json()
        return _persist_dispatch_result(run_id=run_id, task_id=task_id, result_data=result_data)

    except httpx.ConnectError:
        logger.error("dispatch: CLI Agent not reachable at %s", a2a_url)
        RunsRepo.update_run_status(run_id, "failed")
        RunsRepo.save_outcome(
            run_id=run_id,
            task_id=task_id,
            status="failed",
            error_code="internal_error",
            error_message=f"CLI Agent not reachable at {a2a_url}",
        )
        return {
            "dispatch_status": "cli_agent_unreachable",
            "dispatch_result": {
                "state": "failed",
                "message": f"CLI Agent not reachable at {a2a_url}",
                "error_code": "internal_error",
            },
        }

    except Exception as exc:
        logger.exception("dispatch: failed task=%s", task_id)
        RunsRepo.update_run_status(run_id, "failed")
        RunsRepo.save_outcome(
            run_id=run_id,
            task_id=task_id,
            status="failed",
            summary="Dispatch failed",
            error_code="internal_error",
            error_message=str(exc),
        )
        return {
            "dispatch_status": f"error: {exc}",
            "dispatch_result": {
                "state": "failed",
                "message": str(exc),
                "error_code": "internal_error",
            },
        }


def dispatch(state: AgentState) -> AgentState:
    """Dispatch the packaged task to the CLI Agent over A2A."""
    run_id = state["run_id"]
    task_id = state.get("task_id")
    payload = state.get("payload")

    if not payload or not task_id:
        logger.info("dispatch: nothing to dispatch (run=%s)", run_id)
        return {**state, "dispatch_status": "skipped_no_payload"}

    result = dispatch_payload(run_id=run_id, task_id=task_id, payload=payload)
    return {**state, **result}


def _build_a2a_request(*, task_id: str, payload) -> dict:
    message = Message(
        role=Role.USER,
        parts=[
            TextPart(text=payload.prompt),
            DataPart(data={"taskPayload": payload.model_dump()}),
        ],
        taskId=task_id,
        contextId=payload.run_id,
        metadata={"assistant": payload.assistant, "repository": payload.repository},
    )
    params = MessageSendParams(
        message=message,
        configuration=MessageSendConfiguration(
            blocking=True,
            historyLength=2,
            acceptedOutputModes=["application/json", "text/plain"],
        ),
    )
    request = JSONRPCRequest(
        id=uuid4().hex,
        method="message/send",
        params=params.model_dump(by_alias=True, exclude_none=True),
    )
    return request.model_dump(exclude_none=True)


def _convert_a2a_response(response_data: dict) -> dict:
    if "error" in response_data:
        error = response_data.get("error", {})
        message = error.get("message", "A2A request failed.")
        return {
            "state": "failed",
            "summary": message,
            "message": message,
            "error_code": "internal_error",
            "artifacts": [],
        }

    task = Task.model_validate(response_data.get("result", {}))
    output = _extract_artifact_text(task)
    summary = _extract_status_text(task) or output or "Task completed."
    metadata = task.metadata or {}

    return {
        "task_id": task.id,
        "state": task.status.state.value,
        "summary": summary,
        "output": output,
        "artifacts": [
            artifact.model_dump(by_alias=True, exclude_none=True) for artifact in task.artifacts
        ],
        "duration_seconds": metadata.get("durationSeconds"),
        "error_code": metadata.get("errorCode"),
        "message": summary,
    }


def _extract_status_text(task: Task) -> str:
    if not task.status.message:
        return ""
    texts = [
        part.text for part in task.status.message.parts if isinstance(part, TextPart) and part.text
    ]
    return "\n".join(texts).strip()


def _extract_artifact_text(task: Task) -> str:
    texts: list[str] = []
    for artifact in task.artifacts:
        for part in artifact.parts:
            if isinstance(part, TextPart) and part.text:
                texts.append(part.text)
    return "\n\n".join(texts).strip()


def _persist_dispatch_result(*, run_id: str, task_id: str, result_data: dict) -> dict:
    result_state = result_data.get("state", "unknown")
    if result_state == "completed":
        RunsRepo.update_run_status(run_id, "completed")
        RunsRepo.save_outcome(
            run_id=run_id,
            task_id=task_id,
            status="completed",
            summary=result_data.get("summary"),
            output=result_data.get("output", "")[:10000],
            artifacts=result_data.get("artifacts", []),
            duration_seconds=result_data.get("duration_seconds"),
        )
    elif result_state == "failed":
        RunsRepo.update_run_status(run_id, "failed")
        RunsRepo.save_outcome(
            run_id=run_id,
            task_id=task_id,
            status="failed",
            summary=result_data.get("summary"),
            output=result_data.get("output", ""),
            error_code=result_data.get("error_code"),
            error_message=result_data.get("message"),
        )
    else:
        RunsRepo.update_run_status(run_id, "failed")
        RunsRepo.save_outcome(
            run_id=run_id,
            task_id=task_id,
            status="failed",
            summary=result_data.get("message", "Unknown error"),
            error_code=result_data.get("error_code", "internal_error"),
            error_message=result_data.get("message"),
        )

    logger.info(
        "dispatch: completed task=%s state=%s (run=%s)",
        task_id,
        result_state,
        run_id,
    )
    return {"dispatch_status": result_state, "dispatch_result": result_data}
