"""Repository layer for approvals."""

from contextsuite_agent.persistence.client import get_supabase


class ApprovalsRepo:
    """CRUD operations for approvals."""

    @staticmethod
    def create_approval(
        *,
        run_id: str,
        decision: str,
        risk: str = "low",
        reason: str | None = None,
        reviewer: str = "auto",
        policy_violations: list[str] | None = None,
    ) -> dict:
        data: dict = {
            "run_id": run_id,
            "decision": decision,
            "risk": risk,
            "reviewer": reviewer,
            "policy_violations": policy_violations or [],
        }
        if reason:
            data["reason"] = reason
        result = get_supabase().table("approvals").insert(data).execute()
        return result.data[0]

    @staticmethod
    def get_approval_for_run(run_id: str) -> dict | None:
        result = get_supabase().table("approvals").select("*").eq("run_id", run_id).execute()
        return result.data[0] if result.data else None
