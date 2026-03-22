"""Plan generation node — uses Gemini to create a task plan from prompt + context."""

from __future__ import annotations

import logging

from google import genai

from contextsuite_agent.config import settings
from contextsuite_agent.persistence import RunsRepo
from contextsuite_agent.workflow.state import AgentState

logger = logging.getLogger(__name__)

PLAN_SYSTEM_PROMPT = """\
You are the planning module of ContextSuite, a governance layer for AI coding workflows.

Given a developer prompt and retrieved project context, generate a concise task plan.

The plan should:
1. Summarize what needs to be done (1-2 sentences)
2. List the specific steps (3-7 bullet points)
3. Note any files likely to be modified
4. Flag any risks or constraints from the context

Keep the plan actionable and focused. Do not include code — just the plan.
"""


def plan(state: AgentState) -> AgentState:
    """Generate a task plan using Gemini based on prompt + context."""
    prompt = state["prompt"]
    run_id = state["run_id"]
    context_summary = state.get("context_summary", "No context available.")

    logger.info("plan: generating plan for run=%s", run_id)

    user_message = (
        f"## Developer Prompt\n{prompt}\n\n"
        f"## Retrieved Context\n{context_summary}"
    )

    client = genai.Client(api_key=settings.google_api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message,
        config=genai.types.GenerateContentConfig(
            system_instruction=PLAN_SYSTEM_PROMPT,
            temperature=0.3,
            max_output_tokens=1024,
        ),
    )

    plan_text = response.text.strip() if response.text else "Plan generation failed."
    logger.info("plan: generated plan (%d chars) for run=%s", len(plan_text), run_id)

    # Persist the plan
    RunsRepo.save_plan(run_id=run_id, content=plan_text)

    # Move to reviewing
    RunsRepo.update_run_status(run_id, "reviewing")

    return {**state, "plan": plan_text}
