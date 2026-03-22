"""Repository layer for prompts."""

from contextsuite_agent.persistence.client import get_supabase


class PromptsRepo:
    """CRUD operations for prompts."""

    @staticmethod
    def create_prompt(
        *, run_id: str, content: str, repository_id: str | None = None, assistant: str = "codex"
    ) -> dict:
        data: dict = {"run_id": run_id, "content": content, "assistant": assistant}
        if repository_id:
            data["repository_id"] = repository_id
        result = get_supabase().table("prompts").insert(data).execute()
        return result.data[0]

    @staticmethod
    def get_prompt_for_run(run_id: str) -> dict | None:
        result = get_supabase().table("prompts").select("*").eq("run_id", run_id).execute()
        return result.data[0] if result.data else None
