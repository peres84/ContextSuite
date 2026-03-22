"""HTTP and A2A server for the Context Agent."""

from __future__ import annotations

import logging
import time

import uvicorn
from contextsuite_shared.a2a import (
    A2A_TASK_NOT_RESUMABLE,
    JSONRPC_INVALID_PARAMS,
    JSONRPC_INVALID_REQUEST,
    JSONRPC_METHOD_NOT_FOUND,
    JSONRPCRequest,
    MessageSendParams,
    TaskQueryParams,
)
from contextsuite_shared.logutils import configure_logging
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from contextsuite_agent.a2a import (
    build_agent_card,
    build_task_from_result,
    can_resume_task,
    ensure_assistant_id,
    extract_approval_response,
    extract_submission,
    get_persisted_task,
    jsonrpc_error,
    jsonrpc_success,
    task_not_found_error,
)
from contextsuite_agent.config import settings

configure_logging(service="context-agent", level=settings.context_agent_log_level)
request_logger = logging.getLogger("server.http")

app = FastAPI(
    title="ContextSuite Context Agent",
    version="0.1.0",
    description="Context, governance, and memory layer for AI coding workflows",
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    request_logger.info("start %s %s", request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = (time.perf_counter() - start) * 1000
        request_logger.exception(
            "fail %s %s in %.0fms",
            request.method,
            request.url.path,
            elapsed_ms,
        )
        raise

    elapsed_ms = (time.perf_counter() - start) * 1000
    request_logger.info(
        "done %s %s status=%s in %.0fms",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


class TaskRequest(BaseModel):
    """Request body for submitting a task to the Context Agent."""

    prompt: str
    repository: str | None = None
    assistant: str = "codex"
    workspace_path: str | None = None


class ApprovalResolutionRequest(BaseModel):
    """Request body for resolving an escalated approval."""

    approved: bool
    reviewer: str = "human-cli"
    reason: str | None = None
    workspace_path: str | None = None


def build_task_response(result: dict) -> dict:
    """Serialize workflow state for API consumers."""
    approval = result.get("approval")
    risk = result.get("risk")
    execution = result.get("dispatch_result")
    saved_memory = result.get("saved_memory")

    if approval and getattr(approval, "status", None) == "escalated":
        status = "pending_human_approval"
    else:
        status = result.get("dispatch_status", "unknown")

    return {
        "run_id": result.get("run_id"),
        "trace_id": result.get("trace_id"),
        "assistant": result.get("assistant"),
        "status": status,
        "plan": result.get("plan"),
        "context_summary": result.get("context_summary"),
        "risk": {
            "level": risk.level if risk else "low",
            "reason": risk.reason if risk else "",
            "signals": [s.signal for s in risk.signals] if risk and risk.signals else [],
        },
        "approval": {
            "approved": approval.approved if approval else False,
            "status": str(approval.status) if approval else "rejected",
            "reason": approval.reason if approval else "",
            "reviewer": approval.reviewer if approval else "",
            "policy_violations": approval.policy_violations if approval else [],
            "requires_human_approval": bool(approval and str(approval.status) == "escalated"),
        },
        "task_id": result.get("task_id"),
        "execution": execution,
        "saved_memory": saved_memory,
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "context-agent"}


def _base_url(request: Request) -> str:
    return str(request.base_url).rstrip("/")


def _agent_card_payload(base_url: str) -> dict:
    return build_agent_card(base_url).model_dump(by_alias=True, exclude_none=True)


@app.get("/.well-known/agent-card.json")
async def agent_card(request: Request, assistant_id: str | None = None):
    if assistant_id:
        try:
            ensure_assistant_id(assistant_id)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _agent_card_payload(_base_url(request))


@app.get("/.well-known/agent.json")
async def legacy_agent_card(request: Request, assistant_id: str | None = None):
    return await agent_card(request, assistant_id=assistant_id)


@app.get("/a2a/{assistant_id}/.well-known/agent-card.json")
async def scoped_agent_card(request: Request, assistant_id: str):
    try:
        ensure_assistant_id(assistant_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _agent_card_payload(_base_url(request))


@app.post("/tasks/send")
async def send_task(request: TaskRequest):
    """Submit a prompt through the full Context Agent workflow."""
    from contextsuite_agent.workflow import workflow

    result = workflow.invoke(
        {
            "prompt": request.prompt,
            "repository": request.repository,
            "assistant": request.assistant,
            "workspace_path": request.workspace_path,
        }
    )
    return build_task_response(result)


@app.post("/tasks/{run_id}/approval")
async def resolve_approval(run_id: str, request: ApprovalResolutionRequest):
    """Resolve a human approval checkpoint and continue the run if approved."""
    from contextsuite_agent.persistence import ApprovalsRepo
    from contextsuite_agent.workflow.resume import resolve_human_approval

    latest = ApprovalsRepo.get_approval_for_run(run_id)
    if not latest:
        raise HTTPException(status_code=404, detail=f"No approval record found for run {run_id}")
    if latest.get("decision") != "escalated":
        raise HTTPException(
            status_code=409,
            detail=f"Run {run_id} is not awaiting human approval",
        )

    try:
        result = resolve_human_approval(
            run_id=run_id,
            approved=request.approved,
            reviewer=request.reviewer,
            reason=request.reason,
            workspace_path=request.workspace_path,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return build_task_response(result)


@app.post("/a2a/{assistant_id}")
async def a2a_endpoint(assistant_id: str, request: dict):
    """Handle A2A JSON-RPC requests for the Context Agent."""
    try:
        ensure_assistant_id(assistant_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        rpc_request = JSONRPCRequest.model_validate(request)
    except Exception as exc:
        return jsonrpc_error(
            None,
            code=JSONRPC_INVALID_REQUEST,
            message="Invalid JSON-RPC request.",
            data=str(exc),
        )

    if rpc_request.jsonrpc != "2.0":
        return jsonrpc_error(
            rpc_request.id,
            code=JSONRPC_INVALID_REQUEST,
            message="Only JSON-RPC 2.0 is supported.",
        )

    if rpc_request.method == "message/send":
        return await _handle_message_send(rpc_request)
    if rpc_request.method == "tasks/get":
        return _handle_tasks_get(rpc_request)
    if rpc_request.method == "message/stream":
        return jsonrpc_error(
            rpc_request.id,
            code=JSONRPC_METHOD_NOT_FOUND,
            message="message/stream is not implemented by this agent.",
        )

    return jsonrpc_error(
        rpc_request.id,
        code=JSONRPC_METHOD_NOT_FOUND,
        message=f"Unsupported A2A method: {rpc_request.method}",
    )


async def _handle_message_send(rpc_request: JSONRPCRequest) -> dict:
    from contextsuite_agent.persistence import RunsRepo
    from contextsuite_agent.workflow import workflow
    from contextsuite_agent.workflow.resume import resolve_human_approval

    try:
        params = MessageSendParams.model_validate(rpc_request.params or {})
    except Exception as exc:
        return jsonrpc_error(
            rpc_request.id,
            code=JSONRPC_INVALID_PARAMS,
            message="Invalid parameters for message/send.",
            data=str(exc),
        )

    history_length = params.configuration.history_length if params.configuration else None
    message = params.message

    if message.task_id:
        if RunsRepo.get_run(message.task_id) is None:
            return task_not_found_error(rpc_request.id, message.task_id)
        if not can_resume_task(message.task_id):
            return jsonrpc_error(
                rpc_request.id,
                code=A2A_TASK_NOT_RESUMABLE,
                message=f"Task {message.task_id} is not awaiting additional input.",
            )

        decision = extract_approval_response(message)
        if not decision:
            return jsonrpc_error(
                rpc_request.id,
                code=JSONRPC_INVALID_PARAMS,
                message=(
                    "Approval continuations must include a data part with "
                    "`approved`, `reviewer`, and optional `reason`."
                ),
            )

        try:
            result = resolve_human_approval(run_id=message.task_id, **decision)
        except ValueError:
            return task_not_found_error(rpc_request.id, message.task_id)

        task = build_task_from_result(result, message, history_length=history_length)
        return jsonrpc_success(rpc_request.id, task.model_dump(by_alias=True, exclude_none=True))

    try:
        submission = extract_submission(message, params.metadata)
    except ValueError as exc:
        return jsonrpc_error(
            rpc_request.id,
            code=JSONRPC_INVALID_PARAMS,
            message=str(exc),
        )

    result = workflow.invoke(submission)
    task = build_task_from_result(result, message, history_length=history_length)
    return jsonrpc_success(rpc_request.id, task.model_dump(by_alias=True, exclude_none=True))


def _handle_tasks_get(rpc_request: JSONRPCRequest) -> dict:
    try:
        params = TaskQueryParams.model_validate(rpc_request.params or {})
    except Exception as exc:
        return jsonrpc_error(
            rpc_request.id,
            code=JSONRPC_INVALID_PARAMS,
            message="Invalid parameters for tasks/get.",
            data=str(exc),
        )

    try:
        task = get_persisted_task(params.id, history_length=params.history_length)
    except LookupError:
        return task_not_found_error(rpc_request.id, params.id)

    return jsonrpc_success(rpc_request.id, task.model_dump(by_alias=True, exclude_none=True))


def main():
    uvicorn.run(
        "contextsuite_agent.server:app",
        host=settings.context_agent_host,
        port=settings.context_agent_port,
        reload=settings.context_agent_reload,
        log_config=None,
        access_log=False,
    )


if __name__ == "__main__":
    main()
