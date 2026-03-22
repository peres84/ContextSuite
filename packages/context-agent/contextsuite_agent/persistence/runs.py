"""Repository layer for runs, plans, context snapshots, and outcomes."""

from contextsuite_agent.persistence.client import get_supabase


class RunsRepo:
    """CRUD operations for runs and related tables."""

    @staticmethod
    def create_run(*, repository_id: str | None = None, assistant: str = "codex") -> dict:
        data: dict = {"assistant": assistant}
        if repository_id:
            data["repository_id"] = repository_id
        result = get_supabase().table("runs").insert(data).execute()
        return result.data[0]

    @staticmethod
    def get_run(run_id: str) -> dict | None:
        result = get_supabase().table("runs").select("*").eq("id", run_id).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def update_run_status(run_id: str, status: str, **kwargs) -> dict:
        data: dict = {"status": status, **kwargs}
        result = get_supabase().table("runs").update(data).eq("id", run_id).execute()
        return result.data[0]

    @staticmethod
    def save_plan(*, run_id: str, content: str, version: int = 1) -> dict:
        result = (
            get_supabase()
            .table("plans")
            .insert({"run_id": run_id, "content": content, "version": version})
            .execute()
        )
        return result.data[0]

    @staticmethod
    def get_latest_plan(run_id: str) -> dict | None:
        result = (
            get_supabase()
            .table("plans")
            .select("*")
            .eq("run_id", run_id)
            .order("version", desc=True)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    @staticmethod
    def save_context_snapshot(*, run_id: str, summary: str, sources: list | None = None) -> dict:
        result = (
            get_supabase()
            .table("context_snapshots")
            .insert({"run_id": run_id, "summary": summary, "sources": sources or []})
            .execute()
        )
        return result.data[0]

    @staticmethod
    def get_latest_context_snapshot(run_id: str) -> dict | None:
        result = (
            get_supabase()
            .table("context_snapshots")
            .select("*")
            .eq("run_id", run_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    @staticmethod
    def save_outcome(
        *,
        run_id: str,
        task_id: str | None = None,
        status: str,
        summary: str | None = None,
        output: str | None = None,
        artifacts: list | None = None,
        duration_seconds: float | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> dict:
        data: dict = {"run_id": run_id, "status": status}
        if task_id:
            data["task_id"] = task_id
        if summary:
            data["summary"] = summary
        if output:
            data["output"] = output
        if artifacts:
            data["artifacts"] = artifacts
        if duration_seconds is not None:
            data["duration_seconds"] = duration_seconds
        if error_code:
            data["error_code"] = error_code
        if error_message:
            data["error_message"] = error_message
        result = get_supabase().table("outcomes").insert(data).execute()
        return result.data[0]

    @staticmethod
    def get_latest_outcome(run_id: str) -> dict | None:
        result = (
            get_supabase()
            .table("outcomes")
            .select("*")
            .eq("run_id", run_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    @staticmethod
    def list_runs(limit: int = 20) -> list[dict]:
        result = (
            get_supabase()
            .table("runs")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data
