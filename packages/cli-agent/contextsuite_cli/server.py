"""Local A2A listener for the CLI Agent."""

import logging

import uvicorn
from fastapi import FastAPI

from contextsuite_cli.config import settings

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


@app.get("/.well-known/agent.json")
async def agent_card():
    from contextsuite_shared.agent_card import build_cli_agent_card

    base_url = f"http://{settings.cli_agent_host}:{settings.cli_agent_port}"
    card = build_cli_agent_card(base_url)
    return card.model_dump()


@app.post("/tasks/receive")
async def receive_task(request: dict):
    """Receive an A2A task from the Context Agent and execute it.

    Expects: { task_id, payload: TaskPayload }
    Returns: TaskResult or TaskError
    """
    from contextsuite_shared.a2a import TaskPayload
    from contextsuite_shared.a2a.error import ErrorCode, TaskError

    from contextsuite_cli.adapters import get_adapter
    from contextsuite_cli.executor import execute_task

    task_id = request.get("task_id", "")
    payload_data = request.get("payload", {})

    try:
        payload = TaskPayload(**payload_data)
    except Exception as e:
        return TaskError(
            task_id=task_id,
            error_code=ErrorCode.INTERNAL_ERROR,
            message=f"Invalid payload: {e}",
        ).model_dump()

    # Select adapter
    adapter = get_adapter(payload.assistant)
    if adapter is None:
        return TaskError(
            task_id=task_id,
            error_code=ErrorCode.ADAPTER_NOT_FOUND,
            message=f"No adapter for assistant '{payload.assistant}'",
            run_id=payload.run_id,
            trace_id=payload.trace_id,
        ).model_dump()

    # Execute
    result = await execute_task(task_id, payload, adapter)
    return result.model_dump()


def main():
    uvicorn.run(
        "contextsuite_cli.server:app",
        host=settings.cli_agent_host,
        port=settings.cli_agent_port,
        reload=True,
    )


if __name__ == "__main__":
    main()
