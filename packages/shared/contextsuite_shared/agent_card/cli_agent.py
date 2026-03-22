"""Agent Card for the CLI Agent aligned with the A2A spec."""

from __future__ import annotations

from contextsuite_shared.agent_card.context_agent import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentProvider,
    AgentSkill,
)

CLI_AGENT_ID = "contextsuite-cli-agent"


def build_cli_agent_card(base_url: str = "http://localhost:8001") -> AgentCard:
    """Build the Agent Card for the CLI Agent."""
    endpoint = f"{base_url}/a2a/{CLI_AGENT_ID}"
    return AgentCard(
        name="ContextSuite CLI Agent",
        description=(
            "Local agent client that receives approved ContextSuite tasks and runs "
            "Codex, Claude Code, or Cursor through a real A2A JSON-RPC endpoint."
        ),
        url=endpoint,
        preferredTransport="JSONRPC",
        additionalInterfaces=[AgentInterface(url=endpoint, transport="JSONRPC")],
        provider=AgentProvider(url=base_url),
        documentationUrl=f"{base_url}/docs",
        capabilities=AgentCapabilities(
            streaming=False,
            pushNotifications=False,
            stateTransitionHistory=False,
        ),
        defaultInputModes=["application/json", "text/plain"],
        defaultOutputModes=["application/json", "text/plain"],
        skills=[
            AgentSkill(
                id="task-execution",
                name="Task Execution",
                description="Execute coding tasks using a selected CLI assistant.",
                tags=["execution", "cli", "coding"],
                inputModes=["application/json", "text/plain"],
                outputModes=["application/json", "text/plain"],
            ),
            AgentSkill(
                id="artifact-capture",
                name="Artifact Capture",
                description=(
                    "Return execution summaries, logs, and artifacts from the selected assistant."
                ),
                tags=["artifacts", "logs", "results"],
                inputModes=["application/json"],
                outputModes=["application/json", "text/plain"],
            ),
            AgentSkill(
                id="task-polling",
                name="Task Polling",
                description="Expose `tasks/get` for recently executed local tasks.",
                tags=["tasks", "polling", "status"],
                inputModes=["application/json"],
                outputModes=["application/json"],
            ),
        ],
    )


CLI_AGENT_CARD = build_cli_agent_card()
