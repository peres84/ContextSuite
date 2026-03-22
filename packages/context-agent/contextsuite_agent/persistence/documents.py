"""Document ingestion metadata repository."""

from __future__ import annotations

from contextsuite_agent.persistence.client import get_supabase


class DocumentsRepo:
    """CRUD operations for the documents table (ingestion tracking)."""

    @staticmethod
    def create_document(
        *,
        repository_id: str | None,
        source_type: str,
        content: str,
        source_path: str | None = None,
        title: str | None = None,
        chunk_index: int = 0,
        chunk_total: int = 1,
        vector_id: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        sb = get_supabase()
        result = (
            sb.table("documents")
            .insert({
                "repository_id": repository_id,
                "source_type": source_type,
                "source_path": source_path,
                "title": title,
                "content": content,
                "chunk_index": chunk_index,
                "chunk_total": chunk_total,
                "vector_id": vector_id,
                "metadata": metadata or {},
            })
            .execute()
        )
        return result.data[0]

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
