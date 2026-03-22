"""Local A2A listener for the CLI Agent."""

import uvicorn
from fastapi import FastAPI

from contextsuite_cli.config import settings

app = FastAPI(
    title="ContextSuite CLI Agent",
    version="0.1.0",
    description="Local agent client for running coding assistant CLIs",
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "cli-agent"}


@app.get("/.well-known/agent.json")
async def agent_card():
    from contextsuite_shared.agent_card import build_cli_agent_card

    base_url = f"http://{settings.cli_agent_host}:{settings.cli_agent_port}"
    card = build_cli_agent_card(base_url)
    return card.model_dump()


def main():
    uvicorn.run(
        "contextsuite_cli.server:app",
        host=settings.cli_agent_host,
        port=settings.cli_agent_port,
        reload=True,
    )


if __name__ == "__main__":
    main()
