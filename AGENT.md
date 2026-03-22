# AGENT.md

This file is the agent-facing working brief for this repository.

Use it with the human-facing `README.md`. For implementation work, read the current workflow docs before changing architecture or transport behavior.

## Project State

ContextSuite is a context, governance, and memory layer for AI coding workflows.

The current shipped flow is:

1. A prompt reaches the Context Agent through legacy HTTP or real A2A JSON-RPC.
2. The Context Agent retrieves context, generates a plan, classifies risk, and applies approval rules.
3. Approved work is packaged into a shared `TaskPayload`.
4. The Context Agent dispatches to the CLI Agent, preferring A2A and falling back to legacy HTTP only for compatibility.
5. The CLI Agent runs a local coding assistant CLI.
6. Outcomes and issue memory are persisted for later retrieval.

## Source Of Truth

Read these before making meaningful changes:

- `README.md`: current setup, commands, and operator-facing overview
- `docs/workflow.md`: workflow stages, approval behavior, and A2A mapping
- `docs/pipeline.md`: run, test, and verification guide
- `docs/user-guideline.md`: exact manual test prompts and payloads
- `docs/architecture.md`: monorepo layout and runtime responsibilities
- `KNOWN_ISSUES.md`: current gaps and compatibility limits
- `docs/plan.md`: tracked MVP checklist and remaining work

## Locked Decisions

Do not change these unless the user explicitly asks:

- Real A2A JSON-RPC is the primary interoperability surface.
- Legacy HTTP endpoints stay available unless they are intentionally replaced.
- Business logic stays in the existing workflow; transport compatibility should be solved with adapter layers first.
- MCP is optional and internal, not the main ContextSuite-to-executor transport.
- Supabase is the relational system of record.
- Qdrant Cloud is the vector store.
- Neo4j Aura is the graph store.
- Gemini Embedding 2 is used for embeddings.
- Backend and agent code stays in Python.

## Current A2A Status

Implemented now:

- agent card discovery
- `/a2a/{assistant_id}` on both agents
- JSON-RPC `message/send`
- JSON-RPC `tasks/get`
- approval continuation through follow-up A2A `message/send`
- Context Agent to CLI Agent dispatch over A2A with legacy fallback

Still not implemented:

- `message/stream`
- push notifications
- non-blocking/background A2A execution
- persisted CLI Agent task state across restarts

## Working Rules

- Preserve the existing workflow, approvals, memory saving, and adapter behavior unless the user asks for a product change.
- If you touch A2A models, align them to the actual wire protocol rather than keeping old custom shapes.
- If you change routes or contracts, update tests and docs in the same turn.
- Keep `docs/user-guideline.md`, `docs/workflow.md`, and `KNOWN_ISSUES.md` aligned with real behavior.
- Do not assume that a local project path means repository memory exists; ingestion is separate from workspace execution.
- Prefer small adapter-layer changes over broad rewrites.

## Repository Layout

- `packages/shared/`: shared contracts, A2A models, agent cards, and types
- `packages/context-agent/`: Context Agent server, workflow, retrieval, persistence, ingestion
- `packages/cli-agent/`: CLI Agent server, A2A adapter, task store, executor, assistant adapters
- `packages/cli-app/`: terminal client used for manual and demo flows
- `scripts/`: setup, ingestion, connectivity checks, and demo helpers
- `docs/`: operator, workflow, pipeline, and architecture documentation

## Testing And Validation

- Run `uv run ruff check .` for linting when code changes are involved.
- Run `uv run pytest` when behavior or contracts change.
- For doc-only updates, do not claim tests were rerun unless you actually reran them.
- For protocol changes, add or update tests for both the shared contract layer and the server behavior.

## If You Are Unsure What To Do Next

Start with:

1. `docs/workflow.md`
2. `docs/pipeline.md`
3. `docs/plan.md`

Then continue the next piece of work that improves the real end-to-end path without breaking the current working product.
