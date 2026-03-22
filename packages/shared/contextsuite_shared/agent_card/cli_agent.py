"""Agent Card for the CLI Agent (Local Client) — A2A spec compliant."""

from contextsuite_shared.agent_card.context_agent import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentProvider,
    AgentSkill,
)


def build_cli_agent_card(base_url: str = "http://localhost:8001") -> AgentCard:
    """Build the Agent Card for the CLI Agent."""
    return AgentCard(
        id="contextsuite-cli-agent",
        name="ContextSuite CLI Agent",
        description=(
            "Local agent client that receives A2A tasks and runs coding assistant CLIs "
            "(Codex, Claude Code, Cursor)."
        ),
        provider=AgentProvider(),
        capabilities=AgentCapabilities(streaming=True, push_notifications=False, multi_turn=False),
        skills=[
            AgentSkill(
                id="task-execution",
                name="Task Execution",
                description="Execute coding tasks using a selected CLI assistant",
            ),
            AgentSkill(
                id="output-streaming",
                name="Output Streaming",
                description="Stream execution output back to the Context Agent",
            ),
            AgentSkill(
                id="artifact-capture",
                name="Artifact Capture",
                description="Capture logs, patches, and summaries as artifacts",
            ),
        ],
        interfaces=[AgentInterface(url=f"{base_url}/.well-known/agent.json")],
    )


CLI_AGENT_CARD = build_cli_agent_card()
