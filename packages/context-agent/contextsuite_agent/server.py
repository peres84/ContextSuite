"""HTTP/A2A server for the Context Agent."""

import logging

import uvicorn
from fastapi import FastAPI, HTTPException
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


class ApprovalResolutionRequest(BaseModel):
    """Request body for resolving an escalated approval."""

    approved: bool
    reviewer: str = "human-cli"
    reason: str | None = None


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


@app.get("/.well-known/agent.json")
async def agent_card():
    from contextsuite_shared.agent_card import build_context_agent_card

    base_url = f"http://{settings.context_agent_host}:{settings.context_agent_port}"
    card = build_context_agent_card(base_url)
    return card.model_dump()


@app.post("/tasks/send")
async def send_task(request: TaskRequest):
    """Submit a prompt through the full Context Agent workflow."""
    from contextsuite_agent.workflow import workflow

    result = workflow.invoke({
        "prompt": request.prompt,
        "repository": request.repository,
        "assistant": request.assistant,
    })
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
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return build_task_response(result)


def main():
    uvicorn.run(
        "contextsuite_agent.server:app",
        host=settings.context_agent_host,
        port=settings.context_agent_port,
        reload=True,
    )


if __name__ == "__main__":
    main()
