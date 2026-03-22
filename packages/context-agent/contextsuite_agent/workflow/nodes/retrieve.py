"""Context retrieval node — gathers relevant context for the prompt."""

from __future__ import annotations

import logging

from contextsuite_agent.persistence import RunsRepo
from contextsuite_agent.retrieval import retrieve_context
from contextsuite_agent.workflow.state import AgentState

logger = logging.getLogger(__name__)


def retrieve(state: AgentState) -> AgentState:
    """Retrieve relevant context from vector + graph stores."""
    prompt = state["prompt"]
    run_id = state["run_id"]
    repo_id = state.get("repository_id")

    logger.info("retrieve: searching context for run=%s", run_id)

    results, summary = retrieve_context(
        prompt, repository_id=repo_id, max_results=8
    )

    logger.info("retrieve: found %d results for run=%s", len(results), run_id)

    # Save context snapshot
    sources = [
        {
            "source": r.source,
            "score": r.score,
            "metadata": r.metadata,
            "content": r.content,
        }
        for r in results
    ]
    RunsRepo.save_context_snapshot(run_id=run_id, summary=summary, sources=sources)

    # Move run to 'planning'
    RunsRepo.update_run_status(run_id, "planning")

    return {**state, "context_summary": summary, "context_sources": sources}
