"""Qdrant Cloud client for vector retrieval."""

from qdrant_client import QdrantClient
from qdrant_client.http.models import PayloadSchemaType
from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct, ScoredPoint

from contextsuite_agent.config import settings

_client: QdrantClient | None = None
_repository_index_ready = False


def get_qdrant() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    return _client


def ensure_repository_id_index() -> None:
    """Create the repository_id payload index when repo-scoped retrieval is used.

    Qdrant requires a payload index for filtered search on hosted collections.
    """
    global _repository_index_ready
    if _repository_index_ready:
        return

    get_qdrant().create_payload_index(
        collection_name=settings.qdrant_collection,
        field_name="repository_id",
        field_schema=PayloadSchemaType.KEYWORD,
    )
    _repository_index_ready = True


def upsert_vectors(points: list[PointStruct]) -> None:
    """Upsert embedding vectors into the collection."""
    if any((point.payload or {}).get("repository_id") for point in points):
        ensure_repository_id_index()
    get_qdrant().upsert(collection_name=settings.qdrant_collection, points=points)


def search_similar(
    vector: list[float],
    limit: int = 5,
    *,
    repository_id: str | None = None,
) -> list[ScoredPoint]:
    """Search for similar vectors by cosine similarity.

    When a repository ID is provided, prefer retrieval scoped to that repository so
    unrelated demo/project documents do not leak into the current context.
    """
    query_filter = None
    if repository_id:
        ensure_repository_id_index()
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="repository_id",
                    match=MatchValue(value=repository_id),
                )
            ]
        )

    return (
        get_qdrant()
        .query_points(
            collection_name=settings.qdrant_collection,
            query=vector,
            query_filter=query_filter,
            limit=limit,
        )
        .points
    )
