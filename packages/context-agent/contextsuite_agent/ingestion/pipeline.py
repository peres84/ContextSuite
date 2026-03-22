"""Ingestion pipeline: chunk → embed → store in Qdrant → track in Supabase."""

from __future__ import annotations

import uuid

from qdrant_client.models import PointStruct

from contextsuite_agent.embeddings import embed_texts
from contextsuite_agent.ingestion.chunker import chunk_document
from contextsuite_agent.ingestion.sources import DocumentSource
from contextsuite_agent.persistence.client import get_supabase
from contextsuite_agent.retrieval.vector import upsert_vectors


def ingest_document(source: DocumentSource) -> list[dict]:
    """Ingest a single document: chunk, embed, store, and track.

    Returns the list of created document records from Supabase.
    """
    chunks = chunk_document(source.content)
    if not chunks:
        return []

    texts = [c.text for c in chunks]
    vectors = embed_texts(texts)

    points: list[PointStruct] = []
    records: list[dict] = []

    for chunk, vector in zip(chunks, vectors):
        vector_id = uuid.uuid4().hex

        point = PointStruct(
            id=vector_id,
            vector=vector,
            payload={
                "content": chunk.text,
                "type": source.source_type.value,
                "title": source.title or "",
                "file": source.source_path or "",
                "repository": source.repository or "",
                "repository_id": source.repository_id or "",
                "chunk_index": chunk.index,
                "chunk_total": chunk.total,
                **(source.metadata or {}),
            },
        )
        points.append(point)

        records.append({
            "repository_id": source.repository_id,
            "source_type": source.source_type.value,
            "source_path": source.source_path,
            "title": source.title,
            "content": chunk.text,
            "chunk_index": chunk.index,
            "chunk_total": chunk.total,
            "vector_id": vector_id,
            "metadata": source.metadata or {},
        })

    # Store vectors in Qdrant
    upsert_vectors(points)

    # Track in Supabase
    sb = get_supabase()
    result = sb.table("documents").insert(records).execute()

    return result.data


def ingest_documents(sources: list[DocumentSource]) -> list[dict]:
    """Ingest multiple documents. Returns all created records."""
    all_records: list[dict] = []
    for source in sources:
        all_records.extend(ingest_document(source))
    return all_records
