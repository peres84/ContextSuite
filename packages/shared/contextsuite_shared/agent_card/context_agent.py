"""Agent Card for the Context Agent aligned with the A2A spec."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AgentProvider(BaseModel):
    """Service provider metadata."""

    organization: str = "ContextSuite"
    url: str = "https://contextsuite.local"


class AgentExtension(BaseModel):
    """Declared A2A protocol extension."""

    uri: str
    description: str | None = None
    required: bool = False
    params: dict[str, Any] | None = None


class AgentCapabilities(BaseModel):
    """A2A capabilities supported by the agent."""

    streaming: bool = False
    push_notifications: bool = Field(default=False, alias="pushNotifications")
    state_transition_history: bool = Field(default=False, alias="stateTransitionHistory")
    extensions: list[AgentExtension] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class AgentSkill(BaseModel):
    """A discrete capability exposed by the agent."""

    id: str
    name: str
    description: str
    tags: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    input_modes: list[str] | None = Field(default=None, alias="inputModes")
    output_modes: list[str] | None = Field(default=None, alias="outputModes")
    security: list[dict[str, list[str]]] | None = None

    model_config = ConfigDict(populate_by_name=True)


class AgentInterface(BaseModel):
    """Supported transport endpoint."""

    url: str
    transport: str = "JSONRPC"


class AgentCard(BaseModel):
    """A2A Agent Card schema."""

    protocol_version: str = Field(default="0.3.0", alias="protocolVersion")
    name: str
    description: str
    url: str
    preferred_transport: str = Field(default="JSONRPC", alias="preferredTransport")
    additional_interfaces: list[AgentInterface] = Field(
        default_factory=list,
        alias="additionalInterfaces",
    )
    icon_url: str | None = Field(default=None, alias="iconUrl")
    provider: AgentProvider | None = None
    version: str = "0.1.0"
    documentation_url: str | None = Field(default=None, alias="documentationUrl")
    capabilities: AgentCapabilities
    security_schemes: dict[str, dict[str, Any]] | None = Field(
        default=None,
        alias="securitySchemes",
    )
    security: list[dict[str, list[str]]] | None = None
    default_input_modes: list[str] = Field(default_factory=list, alias="defaultInputModes")
    default_output_modes: list[str] = Field(default_factory=list, alias="defaultOutputModes")
    skills: list[AgentSkill] = Field(default_factory=list)
    supports_authenticated_extended_card: bool = Field(
        default=False,
        alias="supportsAuthenticatedExtendedCard",
    )
    signatures: list[dict[str, Any]] | None = None

    model_config = ConfigDict(populate_by_name=True)


CONTEXT_AGENT_ID = "contextsuite-context-agent"


def build_context_agent_card(base_url: str = "http://localhost:8000") -> AgentCard:
    """Build the Agent Card for the Context Agent."""
    endpoint = f"{base_url}/a2a/{CONTEXT_AGENT_ID}"
    return AgentCard(
        name="ContextSuite Context Agent",
        description=(
            "Receives developer prompts, retrieves project memory, plans changes, "
            "checks risk, handles human approvals, and dispatches approved work to "
            "a coding assistant through A2A."
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
        defaultInputModes=["text/plain", "application/json"],
        defaultOutputModes=["text/plain", "application/json"],
        skills=[
            AgentSkill(
                id="prompt-intake",
                name="Prompt Intake",
                description="Accept and normalize user prompts into a governed workflow run.",
                tags=["prompt", "intake", "workflow"],
                examples=[
                    "Fix the webhook handler to avoid null email crashes.",
                ],
                inputModes=["text/plain", "application/json"],
                outputModes=["application/json", "text/plain"],
            ),
            AgentSkill(
                id="context-retrieval",
                name="Context Retrieval",
                description="Retrieve relevant incidents, constraints, and project memory.",
                tags=["retrieval", "memory", "context"],
                inputModes=["text/plain", "application/json"],
                outputModes=["application/json", "text/plain"],
            ),
            AgentSkill(
                id="plan-review",
                name="Plan Review",
                description="Generate and review implementation plans before execution.",
                tags=["planning", "review", "governance"],
                inputModes=["text/plain", "application/json"],
                outputModes=["application/json", "text/plain"],
            ),
            AgentSkill(
                id="risk-check",
                name="Risk Classification",
                description="Classify tasks and escalate high-risk work for human approval.",
                tags=["risk", "approval", "governance"],
                inputModes=["text/plain", "application/json"],
                outputModes=["application/json", "text/plain"],
            ),
            AgentSkill(
                id="a2a-dispatch",
                name="A2A Dispatch",
                description=(
                    "Dispatch approved tasks to the local CLI Agent using the A2A protocol."
                ),
                tags=["a2a", "dispatch", "handoff"],
                inputModes=["application/json"],
                outputModes=["application/json", "text/plain"],
            ),
        ],
    )


CONTEXT_AGENT_CARD = build_context_agent_card()
