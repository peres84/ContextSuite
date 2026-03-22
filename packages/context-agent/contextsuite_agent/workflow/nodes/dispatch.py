"""A2A dispatch node - sends the packaged task to the CLI Agent."""

from __future__ import annotations

import logging

import httpx

from contextsuite_agent.config import settings
from contextsuite_agent.persistence import RunsRepo
from contextsuite_agent.workflow.state import AgentState

logger = logging.getLogger(__name__)


def dispatch_payload(*, run_id: str, task_id: str, payload) -> dict:
    """Dispatch a prepared A2A payload to the CLI Agent and persist the outcome."""
    cli_url = f"http://{settings.cli_agent_host}:{settings.cli_agent_port}/tasks/receive"

    logger.info("dispatch: sending task=%s to %s (run=%s)", task_id, cli_url, run_id)

    try:
        response = httpx.post(
            cli_url,
            json={
                "task_id": task_id,
                "payload": payload.model_dump(),
            },
            timeout=330.0,
        )
        response.raise_for_status()
        result_data = response.json()

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

    except httpx.ConnectError:
        logger.error("dispatch: CLI Agent not reachable at %s", cli_url)
        RunsRepo.update_run_status(run_id, "failed")
        RunsRepo.save_outcome(
            run_id=run_id,
            task_id=task_id,
            status="failed",
            error_code="internal_error",
            error_message=f"CLI Agent not reachable at {cli_url}",
        )
        return {
            "dispatch_status": "cli_agent_unreachable",
            "dispatch_result": {
                "state": "failed",
                "message": f"CLI Agent not reachable at {cli_url}",
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
    """Dispatch the packaged task to the CLI Agent over A2A (HTTP)."""
    run_id = state["run_id"]
    task_id = state.get("task_id")
    payload = state.get("payload")

    if not payload or not task_id:
        logger.info("dispatch: nothing to dispatch (run=%s)", run_id)
        return {**state, "dispatch_status": "skipped_no_payload"}

    result = dispatch_payload(run_id=run_id, task_id=task_id, payload=payload)
    return {**state, **result}
