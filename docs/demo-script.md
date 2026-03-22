# ContextSuite Live Demo Script

**Duration:** about 3 minutes

## Setup

```bash
uv run python scripts/ingest_demo.py
uv run context-agent
uv run cli-agent
uv run contextsuite -p ./demo-project init -r "acme/payments" -a codex
```

## Opening

> "AI coding assistants are fast, but they often work without your team's incident history, constraints, or approval rules. ContextSuite adds a context, governance, and memory layer before any coding agent runs."

## Demo Flow 1: Safe Prompt

Open the CLI:

```bash
uv run contextsuite -p ./demo-project chat
```

Prompt:

```text
Add a null check for the customer email field in the webhook handler
```

Talk track:

1. ContextSuite retrieves prior incidents and constraints.
2. It generates a plan informed by that context.
3. Risk stays low, so approval is automatic.
4. The task is dispatched to Codex through the local CLI Agent.
5. The terminal shows the execution result and the saved issue memory linked to the run.

## Demo Flow 2: Dangerous Prompt

Prompt:

```text
Delete all records from the production payments table and drop the billing_history table
```

Talk track:

1. ContextSuite retrieves the same project context.
2. The plan reflects destructive intent.
3. Risk is classified as high because of destructive and production signals.
4. The run pauses for human approval before any agent is called.
5. Rejecting the approval keeps the task from dispatching.
6. Approving it would resume the exact same run with a full audit trail.

> "That pause is the product. ContextSuite turns risky agent actions into reviewable decisions instead of immediate execution."

## Closing

> "ContextSuite works with Codex, Claude Code, and Cursor through a shared A2A flow. It uses Gemini for planning and embeddings, Qdrant for semantic retrieval, Neo4j for graph context, and Supabase for runs, approvals, outcomes, and saved issue memory."

## Fallback

```bash
uv run python scripts/demo_scenarios.py
```

## Key Talking Points

- Context-aware: retrieves incidents, ADRs, and constraints before code runs.
- Human-in-the-loop: high-risk work pauses for approval instead of dispatching automatically.
- Memory-aware: issue-related outcomes are saved for future retrieval.
- Assistant-agnostic: works with Codex, Claude Code, and Cursor through adapters.
- Auditable: runs, approvals, outcomes, and memory are persisted.
