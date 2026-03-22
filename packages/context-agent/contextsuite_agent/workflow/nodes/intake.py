"""Prompt intake node — creates the run and persists the prompt."""

from __future__ import annotations

import logging

from contextsuite_agent.persistence import PromptsRepo, RunsRepo
from contextsuite_agent.workflow.state import AgentState

logger = logging.getLogger(__name__)


def intake(state: AgentState) -> AgentState:
    """Create a new run and persist the incoming prompt."""
    prompt = state["prompt"]
    repository = state.get("repository")
    assistant = state.get("assistant", "codex")

    logger.info("intake: received prompt (%d chars), assistant=%s", len(prompt), assistant)

    # Look up repository ID if a repository name is given
    repo_id = None
    if repository:
        from contextsuite_agent.persistence.client import get_supabase

        sb = get_supabase()
        rows = sb.table("repositories").select("id").eq("name", repository).execute()
        if rows.data:
            repo_id = rows.data[0]["id"]

    # Create the run
    run = RunsRepo.create_run(repository_id=repo_id, assistant=assistant)
    run_id = run["id"]
    trace_id = run["trace_id"]

    logger.info("intake: created run=%s trace=%s", run_id, trace_id)

    # Save the prompt
    PromptsRepo.create_prompt(
        run_id=run_id, content=prompt, repository_id=repo_id, assistant=assistant
    )

    # Move run to 'retrieving'
    RunsRepo.update_run_status(run_id, "retrieving")

    return {
        **state,
        "run_id": run_id,
        "trace_id": trace_id,
        "repository_id": repo_id,
    }
