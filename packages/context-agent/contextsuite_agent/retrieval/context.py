"""High-level context retrieval — combines vector search, graph queries, and ranking."""

from __future__ import annotations

import logging

from contextsuite_agent.embeddings import embed_text
from contextsuite_agent.retrieval.graph import (
    find_constraints_for_repo,
    find_related_issues,
)
from contextsuite_agent.retrieval.ranking import (
    RetrievalResult,
    format_context_summary,
    rank_results,
)
from contextsuite_agent.retrieval.vector import search_similar

logger = logging.getLogger(__name__)


def retrieve_context(
    prompt: str,
    *,
    repository_id: str | None = None,
    file_paths: list[str] | None = None,
    max_results: int = 10,
) -> tuple[list[RetrievalResult], str]:
    """Retrieve relevant context for a prompt.

    Combines:
    1. Semantic search in Qdrant (embed prompt → find similar docs)
    2. Graph queries in Neo4j (issues affecting files, repo constraints)

    Returns (ranked_results, formatted_summary).
    """
    vector_results: list[RetrievalResult] = []
    graph_results: list[RetrievalResult] = []

    # --- Vector search ---
    try:
        query_vector = embed_text(prompt)
        scored_points = search_similar(
            query_vector,
            limit=max_results,
            repository_id=repository_id,
        )

        for point in scored_points:
            payload = point.payload or {}
            vector_results.append(
                RetrievalResult(
                    source="vector",
                    content=payload.get("content", ""),
                    score=point.score,
                    metadata={
                        "type": payload.get("type", ""),
                        "title": payload.get("title", ""),
                        "file": payload.get("file", ""),
                        "repository": payload.get("repository", ""),
                    },
                )
            )
    except Exception:
        logger.exception("Vector search failed")

    # --- Graph queries (best-effort, Neo4j may be unavailable) ---
    try:
        if file_paths:
            for fp in file_paths[:5]:  # limit to avoid excessive queries
                issues = find_related_issues(fp, limit=3)
                for issue in issues:
                    graph_results.append(
                        RetrievalResult(
                            source="graph",
                            content=f"Issue: {issue.get('title', '')} "
                            f"[{issue.get('severity', '')}]",
                            score=0.6,  # fixed score for graph results
                            metadata={
                                "issue_id": issue.get("id", ""),
                                "status": issue.get("status", ""),
                                "file": fp,
                            },
                        )
                    )

        if repository_id:
            constraints = find_constraints_for_repo(repository_id)
            for c in constraints:
                graph_results.append(
                    RetrievalResult(
                        source="graph",
                        content=f"Constraint: {c.get('description', '')}",
                        score=0.5,
                        metadata={
                            "constraint_id": c.get("id", ""),
                            "source": c.get("source", ""),
                        },
                    )
                )
    except Exception:
        logger.warning("Graph queries unavailable (Neo4j may be down)")

    # --- Rank and format ---
    ranked = rank_results(vector_results, graph_results, max_results=max_results)
    summary = format_context_summary(ranked)

    return ranked, summary
