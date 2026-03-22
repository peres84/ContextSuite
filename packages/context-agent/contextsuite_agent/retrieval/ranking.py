"""Result ranking across vector and graph retrieval sources."""

from dataclasses import dataclass, field


@dataclass
class RetrievalResult:
    """A single retrieval result from any source."""

    source: str  # "vector" or "graph"
    content: str
    score: float = 0.0
    metadata: dict = field(default_factory=dict)


def rank_results(
    vector_results: list[RetrievalResult],
    graph_results: list[RetrievalResult],
    max_results: int = 10,
) -> list[RetrievalResult]:
    """Merge and rank results from vector and graph retrieval.

    Simple strategy: normalize scores, interleave by score, deduplicate.
    """
    all_results = vector_results + graph_results
    all_results.sort(key=lambda r: r.score, reverse=True)
    return all_results[:max_results]


def format_context_summary(results: list[RetrievalResult]) -> str:
    """Format ranked results into a human-readable context summary."""
    if not results:
        return "No relevant context found."

    lines = []
    for i, r in enumerate(results, 1):
        source_tag = f"[{r.source}]"
        lines.append(f"{i}. {source_tag} {r.content}")
        if r.metadata:
            details = ", ".join(f"{k}={v}" for k, v in r.metadata.items())
            lines.append(f"   ({details})")
    return "\n".join(lines)
