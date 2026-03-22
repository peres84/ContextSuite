"""Agent Card for the Context Agent — A2A spec compliant."""

from pydantic import BaseModel, Field


class AgentProvider(BaseModel):
    organization: str = "ContextSuite"
    url: str | None = None


class AgentCapabilities(BaseModel):
    streaming: bool = True
    push_notifications: bool = False
    multi_turn: bool = True


class AgentSkill(BaseModel):
    id: str
    name: str
    description: str


class AgentInterface(BaseModel):
    url: str
    protocol: str = "a2a"


class AgentCard(BaseModel):
    """A2A Agent Card schema."""

    id: str
    name: str
    description: str
    provider: AgentProvider
    capabilities: AgentCapabilities
    skills: list[AgentSkill] = Field(default_factory=list)
    interfaces: list[AgentInterface] = Field(default_factory=list)
    version: str = "0.1.0"


def build_context_agent_card(base_url: str = "http://localhost:8000") -> AgentCard:
    """Build the Agent Card for the Context Agent."""
    return AgentCard(
        id="contextsuite-context-agent",
        name="ContextSuite Context Agent",
        description=(
            "Receives user prompts, retrieves project context, reviews plans, "
            "classifies risk, and dispatches approved tasks over A2A."
        ),
        provider=AgentProvider(),
        capabilities=AgentCapabilities(),
        skills=[
            AgentSkill(
                id="prompt-intake",
                name="Prompt Intake",
                description="Accept and normalize user prompts",
            ),
            AgentSkill(
                id="context-retrieval",
                name="Context Retrieval",
                description="Retrieve relevant project memory, constraints, and prior incidents",
            ),
            AgentSkill(
                id="plan-review",
                name="Plan Review",
                description="Generate or review implementation plans",
            ),
            AgentSkill(
                id="risk-check",
                name="Risk Classification",
                description="Classify task risk as low, medium, or high",
            ),
            AgentSkill(
                id="a2a-dispatch",
                name="A2A Dispatch",
                description="Send approved tasks to the CLI Agent over A2A",
            ),
        ],
        interfaces=[AgentInterface(url=f"{base_url}/.well-known/agent.json")],
    )


CONTEXT_AGENT_CARD = build_context_agent_card()
