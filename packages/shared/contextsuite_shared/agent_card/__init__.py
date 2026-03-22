"""Agent Card definitions."""

from contextsuite_shared.agent_card.cli_agent import CLI_AGENT_CARD, build_cli_agent_card
from contextsuite_shared.agent_card.context_agent import (
    CONTEXT_AGENT_CARD,
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentProvider,
    AgentSkill,
    build_context_agent_card,
)

__all__ = [
    "AgentCapabilities",
    "AgentCard",
    "AgentInterface",
    "AgentProvider",
    "AgentSkill",
    "CLI_AGENT_CARD",
    "CONTEXT_AGENT_CARD",
    "build_cli_agent_card",
    "build_context_agent_card",
]
