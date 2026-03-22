"""Qdrant Cloud client for vector retrieval."""

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, ScoredPoint

from contextsuite_agent.config import settings

_client: QdrantClient | None = None


def get_qdrant() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    return _client


def upsert_vectors(points: list[PointStruct]) -> None:
    """Upsert embedding vectors into the collection."""
    get_qdrant().upsert(collection_name=settings.qdrant_collection, points=points)


def search_similar(vector: list[float], limit: int = 5) -> list[ScoredPoint]:
    """Search for similar vectors by cosine similarity."""
    return (
        get_qdrant()
        .query_points(
            collection_name=settings.qdrant_collection,
            query=vector,
            limit=limit,
        )
        .points
    )
