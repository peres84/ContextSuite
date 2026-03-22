"""HTTP/A2A server for the Context Agent."""

import logging

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from contextsuite_agent.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

app = FastAPI(
    title="ContextSuite Context Agent",
    version="0.1.0",
    description="Context, governance, and memory layer for AI coding workflows",
)


class TaskRequest(BaseModel):
    """Request body for submitting a task to the Context Agent."""

    prompt: str
    repository: str | None = None
    assistant: str = "codex"


@app.get("/health")
async def health():
    return {"status": "ok", "service": "context-agent"}


@app.get("/.well-known/agent.json")
async def agent_card():
    from contextsuite_shared.agent_card import build_context_agent_card

    base_url = f"http://{settings.context_agent_host}:{settings.context_agent_port}"
    card = build_context_agent_card(base_url)
    return card.model_dump()


@app.post("/tasks/send")
async def send_task(request: TaskRequest):
    """Submit a prompt through the full Context Agent workflow.

    Pipeline: intake → retrieve → plan → classify → approve → package
    """
    from contextsuite_agent.workflow import workflow

    result = workflow.invoke({
        "prompt": request.prompt,
        "repository": request.repository,
        "assistant": request.assistant,
    })

    # Build response
    approval = result.get("approval")
    risk = result.get("risk")

    return {
        "run_id": result.get("run_id"),
        "trace_id": result.get("trace_id"),
        "status": result.get("dispatch_status", "unknown"),
        "plan": result.get("plan"),
        "context_summary": result.get("context_summary"),
        "risk": {
            "level": risk.level if risk else "low",
            "reason": risk.reason if risk else "",
            "signals": [s.signal for s in risk.signals] if risk and risk.signals else [],
        },
        "approval": {
            "approved": approval.approved if approval else False,
            "reason": approval.reason if approval else "",
            "reviewer": approval.reviewer if approval else "",
        },
        "task_id": result.get("task_id"),
    }


def main():
    uvicorn.run(
        "contextsuite_agent.server:app",
        host=settings.context_agent_host,
        port=settings.context_agent_port,
        reload=True,
    )


if __name__ == "__main__":
    main()
