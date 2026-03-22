# Project Architecture

This document describes the current runtime architecture of the ContextSuite monorepo after the real A2A compatibility work.

## System Overview

ContextSuite has four main runtime pieces:

1. `context-agent`: the cloud-side orchestrator that receives prompts, retrieves context, applies governance, and dispatches approved work.
2. `cli-agent`: the local execution bridge that receives approved tasks and runs Codex, Claude Code, or Cursor on the developer machine.
3. `cli-app`: the human-facing terminal client used for demos and manual operator testing.
4. `shared`: typed contracts used by all three packages, including A2A models and agent cards.

The key architectural rule is unchanged:

- Business logic stays in the existing workflow.
- Protocol handling is layered on top as an adapter.
- Real A2A is now supported on the wire, while legacy HTTP remains available for compatibility.

## Runtime Flow

The end-to-end flow is:

1. A client sends a request to the Context Agent through either:
   - legacy HTTP `POST /tasks/send`, or
   - A2A JSON-RPC `POST /a2a/contextsuite-context-agent`
2. The Context Agent runs the LangGraph workflow:
   - `intake`
   - `retrieve`
   - `plan`
   - `classify`
   - `approve`
   - `package`
   - `dispatch`
   - `save_memory`
3. If the task is approved, the Context Agent packages a shared `TaskPayload`.
4. The dispatch node sends that payload to the CLI Agent by:
   - preferring A2A JSON-RPC `POST /a2a/contextsuite-cli-agent`
   - falling back to legacy `POST /tasks/receive` if needed
5. The CLI Agent selects the requested adapter and runs the local coding assistant CLI.
6. The Context Agent stores outcomes and durable issue memory, then exposes the final state through:
   - the legacy response body, or
   - A2A `tasks/get`

## Transport Surfaces

### Context Agent

External routes:

- `GET /.well-known/agent-card.json`
- `GET /.well-known/agent.json`
- `GET /a2a/{assistant_id}/.well-known/agent-card.json`
- `POST /a2a/contextsuite-context-agent`
- `POST /tasks/send`
- `POST /tasks/{run_id}/approval`
- `GET /health`

Supported A2A methods:

- `message/send`
- `tasks/get`

### CLI Agent

External routes:

- `GET /.well-known/agent-card.json`
- `GET /.well-known/agent.json`
- `GET /a2a/{assistant_id}/.well-known/agent-card.json`
- `POST /a2a/contextsuite-cli-agent`
- `POST /tasks/receive`
- `GET /health`

Supported A2A methods:

- `message/send`
- `tasks/get`

### Current Compatibility Limits

Implemented now:

- agent card discovery
- A2A `message/send`
- A2A `tasks/get`
- approval continuation through a follow-up A2A `message/send`
- Context Agent to CLI Agent A2A dispatch with safe legacy fallback

Still partial:

- `message/stream`
- push notifications
- non-blocking/background A2A execution
- persisted CLI Agent task state across process restarts

## Monorepo Layout

```text
heilbronn-hackathon/
|-- packages/
|   |-- shared/
|   |   |-- contextsuite_shared/
|   |   |   |-- a2a/
|   |   |   |   |-- error.py
|   |   |   |   |-- payload.py
|   |   |   |   |-- result.py
|   |   |   |   |-- rpc.py
|   |   |   |   |-- status.py
|   |   |   |   |-- task.py
|   |   |   |   `-- utils.py
|   |   |   |-- agent_card/
|   |   |   |   |-- cli_agent.py
|   |   |   |   `-- context_agent.py
|   |   |   `-- types/
|   |   |       |-- approval.py
|   |   |       |-- prompt.py
|   |   |       `-- run.py
|   |   `-- tests/
|   |
|   |-- context-agent/
|   |   |-- contextsuite_agent/
|   |   |   |-- a2a.py
|   |   |   |-- config.py
|   |   |   |-- server.py
|   |   |   |-- embeddings/
|   |   |   |-- ingestion/
|   |   |   |   |-- chunker.py
|   |   |   |   |-- pipeline.py
|   |   |   |   `-- sources.py
|   |   |   |-- persistence/
|   |   |   |   |-- approvals.py
|   |   |   |   |-- client.py
|   |   |   |   |-- documents.py
|   |   |   |   |-- prompts.py
|   |   |   |   `-- runs.py
|   |   |   |-- retrieval/
|   |   |   |   |-- context.py
|   |   |   |   |-- graph.py
|   |   |   |   |-- ranking.py
|   |   |   |   `-- vector.py
|   |   |   `-- workflow/
|   |   |       |-- graph.py
|   |   |       |-- resume.py
|   |   |       |-- state.py
|   |   |       `-- nodes/
|   |   |           |-- approve.py
|   |   |           |-- classify.py
|   |   |           |-- dispatch.py
|   |   |           |-- intake.py
|   |   |           |-- memory.py
|   |   |           |-- package.py
|   |   |           |-- plan.py
|   |   |           `-- retrieve.py
|   |   `-- tests/
|   |
|   |-- cli-agent/
|   |   |-- contextsuite_cli/
|   |   |   |-- a2a.py
|   |   |   |-- config.py
|   |   |   |-- server.py
|   |   |   |-- task_store.py
|   |   |   |-- adapters/
|   |   |   |   |-- base.py
|   |   |   |   |-- claude_code.py
|   |   |   |   |-- codex.py
|   |   |   |   |-- cursor.py
|   |   |   |   `-- registry.py
|   |   |   `-- executor/
|   |   |       `-- lifecycle.py
|   |   `-- tests/
|   |
|   `-- cli-app/
|       |-- contextsuite_app/
|       |   |-- attachments.py
|       |   |-- cli.py
|       |   |-- renderer.py
|       |   `-- session.py
|       `-- pyproject.toml
|
|-- scripts/
|-- docs/
|   |-- architecture.md
|   |-- pipeline.md
|   |-- user-guideline.md
|   `-- workflow.md
|-- AGENT.md
|-- CLAUDE.md
`-- README.md
```

## Package Responsibilities

### `packages/shared`

Shared contracts only. No transport logic and no cloud-specific orchestration.

Contains:

- A2A task, status, result, payload, error, and JSON-RPC models
- agent card definitions for both agents
- shared run, approval, and prompt types

### `packages/context-agent`

The cloud-side orchestrator.

Responsibilities:

- request intake
- repository lookup
- context retrieval from Supabase, Qdrant, and Neo4j
- plan generation
- risk classification and approval decisions
- A2A and legacy HTTP request handling
- dispatch to the CLI Agent
- persistence of runs, plans, approvals, outcomes, and saved issue memory

Important files:

- `server.py`: FastAPI app, legacy routes, discovery routes
- `a2a.py`: A2A JSON-RPC adapter layer
- `workflow/graph.py`: LangGraph definition
- `workflow/resume.py`: approval resume path for persisted runs
- `workflow/nodes/dispatch.py`: A2A-first CLI dispatch adapter

### `packages/cli-agent`

The local execution bridge.

Responsibilities:

- expose a local A2A endpoint and a legacy compatibility route
- receive approved tasks from the Context Agent
- run the selected coding assistant CLI
- return normalized execution results
- keep short-lived task state for `tasks/get`

Important files:

- `server.py`: FastAPI app and route registration
- `a2a.py`: CLI-side A2A JSON-RPC adapter
- `task_store.py`: in-memory task tracking for polling
- `executor/lifecycle.py`: adapter execution flow
- `adapters/*.py`: concrete assistant integrations

### `packages/cli-app`

The human-facing terminal application.

Responsibilities:

- initialize local workspace metadata
- send prompts to the Context Agent
- render plan, risk, approval, and outcome information
- support attachments and session display

Current note:

- The CLI app still uses the legacy `POST /tasks/send` path.
- Direct A2A protocol testing is currently done with raw HTTP requests or external clients, not through the CLI app.

## Data Ownership

| Data | Authoritative Store | Notes |
|---|---|---|
| Runs, prompts, plans, approvals, outcomes | Supabase | Main transactional system of record |
| Repository metadata | Supabase | Repository names are labels unless separately ingested |
| Context snapshots | Supabase | Stores retrieval summary and structured sources per run |
| Semantic vectors | Qdrant | Derived from ingested source material and saved issue memory |
| Graph relationships | Neo4j | Related issues, files, and constraints |
| Durable issue memory | Supabase plus Qdrant | Saved after issue-related runs for future retrieval |

## Architectural Rules

- Keep workflow and business logic in the existing LangGraph pipeline.
- Add or change protocol compatibility through adapter layers first.
- Do not remove the legacy HTTP endpoints unless the migration is explicit and tested.
- When A2A and existing internal types disagree, align the implementation to the real wire protocol rather than only renaming local models.
- Keep documentation and tests in sync with protocol changes.
