"""Document ingestion metadata repository."""

from __future__ import annotations

from contextsuite_agent.persistence.client import get_supabase


class DocumentsRepo:
    """CRUD operations for the documents table (ingestion tracking)."""

    @staticmethod
    def list_for_repository(repository_id: str, limit: int = 100) -> list[dict]:
        sb = get_supabase()
        return (
            sb.table("documents")
            .select("*")
            .eq("repository_id", repository_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
            .data
        )

    @staticmethod
    def list_by_source_type(source_type: str, limit: int = 100) -> list[dict]:
        sb = get_supabase()
        return (
            sb.table("documents")
            .select("*")
            .eq("source_type", source_type)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
            .data
        )

    @staticmethod
    def get_by_vector_id(vector_id: str) -> dict | None:
        sb = get_supabase()
        result = (
            sb.table("documents").select("*").eq("vector_id", vector_id).execute()
        )
        return result.data[0] if result.data else None

    @staticmethod
    def count_for_repository(repository_id: str) -> int:
        sb = get_supabase()
        result = (
            sb.table("documents")
            .select("id", count="exact")
            .eq("repository_id", repository_id)
            .execute()
        )
        return result.count or 0
