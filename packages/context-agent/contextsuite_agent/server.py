"""HTTP/A2A server for the Context Agent."""

import uvicorn
from fastapi import FastAPI

from contextsuite_agent.config import settings

app = FastAPI(
    title="ContextSuite Context Agent",
    version="0.1.0",
    description="Context, governance, and memory layer for AI coding workflows",
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "context-agent"}


@app.get("/.well-known/agent.json")
async def agent_card():
    from contextsuite_shared.agent_card import build_context_agent_card

    base_url = f"http://{settings.context_agent_host}:{settings.context_agent_port}"
    card = build_context_agent_card(base_url)
    return card.model_dump()


def main():
    uvicorn.run(
        "contextsuite_agent.server:app",
        host=settings.context_agent_host,
        port=settings.context_agent_port,
        reload=True,
    )


if __name__ == "__main__":
    main()
