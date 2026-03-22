"""Local CLI Agent server with legacy and A2A-compatible endpoints."""

from __future__ import annotations

import logging
from uuid import uuid4

import uvicorn
from contextsuite_shared.a2a import (
    JSONRPC_INVALID_PARAMS,
    JSONRPC_INVALID_REQUEST,
    JSONRPC_METHOD_NOT_FOUND,
    ErrorCode,
    JSONRPCRequest,
    MessageSendParams,
    TaskError,
    TaskPayload,
    TaskQueryParams,
)
from fastapi import FastAPI, HTTPException, Request

from contextsuite_cli.a2a import (
    build_agent_card,
    build_legacy_payload_message,
    build_task_from_execution,
    ensure_assistant_id,
    extract_task_payload,
    jsonrpc_error,
    jsonrpc_success,
    submitted_task,
    task_not_found_error,
    working_task,
)
from contextsuite_cli.config import settings
from contextsuite_cli.task_store import get_task, save_task

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

app = FastAPI(
    title="ContextSuite CLI Agent",
    version="0.1.0",
    description="Local agent client for running coding assistant CLIs",
)


@app.get("/health")
async def health():
    from contextsuite_cli.adapters import list_adapters

    return {
        "status": "ok",
        "service": "cli-agent",
        "adapters": list_adapters(),
    }


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


@app.post("/tasks/receive")
async def receive_task(request: dict):
    """Receive a legacy task payload and execute it."""
    task_id = request.get("task_id") or uuid4().hex
    payload_data = request.get("payload", {})

    try:
        payload = TaskPayload.model_validate(payload_data)
    except Exception as exc:
        return TaskError(
            task_id=task_id,
            error_code=ErrorCode.INTERNAL_ERROR,
            message=f"Invalid payload: {exc}",
        ).model_dump()

    inbound_message = build_legacy_payload_message(task_id, payload)
    result, _task = await _execute_payload(task_id, payload, inbound_message)
    return result.model_dump()


@app.post("/a2a/{assistant_id}")
async def a2a_endpoint(assistant_id: str, request: dict):
    """Handle A2A JSON-RPC requests for the CLI Agent."""
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
    try:
        params = MessageSendParams.model_validate(rpc_request.params or {})
    except Exception as exc:
        return jsonrpc_error(
            rpc_request.id,
            code=JSONRPC_INVALID_PARAMS,
            message="Invalid parameters for message/send.",
            data=str(exc),
        )

    message = params.message
    try:
        payload = extract_task_payload(message, params.metadata)
    except Exception as exc:
        return jsonrpc_error(
            rpc_request.id,
            code=JSONRPC_INVALID_PARAMS,
            message=f"Invalid task payload in message parts: {exc}",
        )

    task_id = message.task_id or uuid4().hex
    context_id = message.context_id or payload.run_id or uuid4().hex
    inbound_message = message.model_copy(update={"task_id": task_id, "context_id": context_id})

    _result, task = await _execute_payload(task_id, payload, inbound_message)
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

    task = get_task(params.id)
    if task is None:
        return task_not_found_error(rpc_request.id, params.id)

    result = task
    if params.history_length and params.history_length > 0:
        result = task.model_copy(update={"history": task.history[-params.history_length :]})

    return jsonrpc_success(rpc_request.id, result.model_dump(by_alias=True, exclude_none=True))


async def _execute_payload(task_id: str, payload: TaskPayload, inbound_message):
    from contextsuite_cli.adapters import get_adapter
    from contextsuite_cli.executor import execute_task

    adapter = get_adapter(payload.assistant)
    if adapter is None:
        error = TaskError(
            task_id=task_id,
            error_code=ErrorCode.ADAPTER_NOT_FOUND,
            message=f"No adapter for assistant '{payload.assistant}'",
            run_id=payload.run_id,
            trace_id=payload.trace_id,
        )
        task = build_task_from_execution(
            task_id=task_id,
            context_id=inbound_message.context_id or payload.run_id or uuid4().hex,
            inbound_message=inbound_message,
            result=error,
        )
        save_task(task)
        return error, task

    task = submitted_task(inbound_message)
    save_task(task)
    task = working_task(task)
    save_task(task)

    result = await execute_task(task_id, payload, adapter)
    final_task = build_task_from_execution(
        task_id=task.id,
        context_id=task.context_id,
        inbound_message=inbound_message,
        result=result,
    )
    save_task(final_task)
    return result, final_task


def main():
    uvicorn.run(
        "contextsuite_cli.server:app",
        host=settings.cli_agent_host,
        port=settings.cli_agent_port,
        reload=settings.cli_agent_reload,
    )


if __name__ == "__main__":
    main()
