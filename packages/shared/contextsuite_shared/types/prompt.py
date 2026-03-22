"""Prompt and plan types."""

from pydantic import BaseModel, Field


class PromptInput(BaseModel):
    """A user prompt submitted to the Context Agent."""

    prompt: str = Field(description="The user's natural language prompt")
    repository: str | None = Field(default=None, description="Target repository")
    assistant: str = Field(default="codex", description="Preferred coding assistant")
