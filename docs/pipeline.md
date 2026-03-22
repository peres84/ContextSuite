# Running and Testing the Pipeline

This document explains how to run, test, and verify the ContextSuite pipeline.

The pipeline can now be exercised through either:

- The legacy HTTP endpoints used by the current CLI/demo flow
- The real A2A JSON-RPC surface at `/a2a/{assistant_id}`

Current transport note:

- The interactive `contextsuite` CLI still uses the legacy `POST /tasks/send` path.
- Use the direct A2A examples below when you want to test the real wire protocol itself.

## Prerequisites

1. **Python 3.12+** and **uv** installed
2. A `.env` file in the project root with all required variables (copy from `.env.example`)
3. Active cloud services: Supabase, Qdrant Cloud, Google AI (Gemini)

## Quick Start

```bash
# Install all dependencies
uv sync --all-packages

# Run the full test suite (no cloud services needed)
uv run pytest -v

# Start the Context Agent server
uv run context-agent

# Start the CLI Agent server in a second terminal
uv run cli-agent
```

## Choose A Test Mode

Before seeding demo data, decide what you want to validate:

- Real local project behavior: skip demo ingestion and point the CLI app at your real workspace with `-p`
- Demo retrieval behavior: seed `acme/payments` so retrieval and saved-memory behavior are visible

Important note:

- The path passed with `-p` controls the local execution workspace.
- The repository label passed with `-r` is metadata unless that repository has actually been ingested.

For exact prompts and exact payloads for both modes, use `docs/user-guideline.md`.

## Service Connectivity Tests

These scripts verify that each cloud service is reachable and configured correctly.

```bash
# Test all services at once
uv run python scripts/test_all.py

# Test individual services
uv run python scripts/test_supabase.py
uv run python scripts/test_qdrant.py
uv run python scripts/test_neo4j.py      # may fail — see KNOWN_ISSUES.md
uv run python scripts/test_gemini.py

# Test the Context Agent and CLI Agent HTTP servers (must be running)
uv run python scripts/test_services.py
```

Neo4j note:

- Use `neo4j+s://`
- Set `NEO4J_DATABASE` to the Aura database ID

## Seeding Demo Data

The demo data represents a fictional `acme/payments` repository with incidents, ADRs, constraints, and code summaries.

Skip this section if you are testing a real local project and want minimal retrieval noise.

### Using the ingestion pipeline (recommended)

```bash
uv run python scripts/ingest_demo.py
```

This runs the full pipeline for 6 demo documents:
1. Chunks each document (paragraph/sentence boundary splitting)
2. Embeds chunks via Gemini Embedding 2 (3072-dim vectors)
3. Stores vectors in Qdrant Cloud (`contextsuite` collection)
4. Tracks metadata in Supabase (`documents` table with `vector_id` cross-reference)
5. Runs a test retrieval query to verify similarity search

Expected output:
```
Using existing repository: 58b29b9e-...
Ingesting 6 documents...
Created 6 document chunks in Supabase + Qdrant
Test retrieval: 10 results
Top result score: 0.81
```

### Setting up Neo4j graph data

After ingesting the demo documents, create the Neo4j schema and seed the graph:

```bash
uv run python scripts/setup_neo4j.py
uv run python scripts/seed_neo4j.py
```

This creates the constraints, indexes, repository nodes, file graph, issues, and constraints used by graph retrieval.

### Using the legacy seed script

```bash
uv run python scripts/seed_data.py
```

This is the older script from Phase 4. It seeds 5 documents directly into Qdrant without using the ingestion pipeline or tracking in Supabase. Prefer `ingest_demo.py` for new work.

## Testing the Workflow

### Start the server

```bash
uv run uvicorn contextsuite_agent.server:app --host 127.0.0.1 --port 8000 --reload
```

In a second terminal, start the CLI Agent:

```bash
uv run cli-agent
```

### Send a low-risk prompt (should be approved)

```bash
curl -X POST http://127.0.0.1:8000/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Fix the webhook handler to validate optional email fields before calling .lower() on them",
    "repository": "acme/payments",
    "assistant": "codex"
  }'
```

Expected: `approval.approved: true`, `status` reaches `completed` when the CLI Agent is running, and `task_id` is set.

### Send the same low-risk prompt through the A2A endpoint

```bash
curl -X POST http://127.0.0.1:8000/a2a/contextsuite-context-agent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-1",
    "method": "message/send",
    "params": {
      "message": {
        "messageId": "msg-1",
        "role": "user",
        "parts": [
          { "kind": "text", "text": "Fix the webhook handler to validate optional email fields before calling .lower() on them" },
          { "kind": "data", "data": { "repository": "acme/payments", "assistant": "codex" } }
        ]
      }
    }
  }'
```

Expected: the JSON-RPC `result` is an A2A `Task` with `status.state: "completed"`, `result.id` equal to the Context Agent `run_id`, and `result.metadata.cliTaskId` populated after dispatch.

### Send a high-risk prompt (should require human approval)

```bash
curl -X POST http://127.0.0.1:8000/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Delete all old payment records from the production database",
    "repository": "acme/payments",
    "assistant": "codex"
  }'
```

Expected: `approval.approved: false`, `approval.status: "escalated"`, `risk.level: "high"`, `status: "pending_human_approval"`, `task_id: null`.

### Approve the escalated run

Use the `run_id` returned by the previous request:

```bash
curl -X POST http://127.0.0.1:8000/tasks/<run-id>/approval \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "reviewer": "human-cli",
    "reason": "Reviewed by operator"
  }'
```

Expected: the run continues to dispatch, `status` reaches `completed` when the CLI Agent is running, and `saved_memory.saved` is `true` when issue-related context was involved.

### Resume the same escalated run through A2A

Use the `result.id` and `result.contextId` returned by the first A2A call:

```bash
curl -X POST http://127.0.0.1:8000/a2a/contextsuite-context-agent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-2",
    "method": "message/send",
    "params": {
      "message": {
        "messageId": "msg-2",
        "taskId": "<run-id>",
        "contextId": "<trace-id>",
        "role": "user",
        "parts": [
          {
            "kind": "data",
            "data": {
              "approval": {
                "approved": true,
                "reviewer": "human-cli",
                "reason": "Reviewed by operator"
              }
            }
          }
        ]
      }
    }
  }'
```

Expected: the JSON-RPC `result.status.state` reaches `completed` when the CLI Agent is running.

### Send a policy-violating prompt (should be blocked)

```bash
curl -X POST http://127.0.0.1:8000/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "drop database tables and start fresh",
    "repository": "acme/payments",
    "assistant": "codex"
  }'
```

Expected: `approval.approved: false`, `approval.reason` mentions "Policy violation".

### Other endpoints

```bash
# Health check
curl http://127.0.0.1:8000/health

# Agent Card (A2A discovery)
curl http://127.0.0.1:8000/.well-known/agent-card.json

# A2A task polling
curl -X POST http://127.0.0.1:8000/a2a/contextsuite-context-agent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-3",
    "method": "tasks/get",
    "params": {
      "id": "<run-id>",
      "historyLength": 2
    }
  }'
```

## Unit Tests

```bash
# Run everything
uv run pytest -v

# Run only contract tests (no cloud services needed)
uv run pytest packages/shared/tests/ -v

# Run only ingestion tests (chunker + sources, no cloud services)
uv run pytest packages/context-agent/tests/test_ingestion.py -v

# Run only workflow tests (risk classification, no cloud services)
uv run pytest packages/context-agent/tests/test_workflow.py -v
```

Current test counts (56 total):
- `test_contracts.py` — 28 tests (A2A schemas, JSON-RPC, agent cards, types)
- `test_ingestion.py` — 9 tests (chunker, document sources)
- `test_workflow.py` — 8 tests (risk classification)
- `test_context_a2a_server.py` — 4 tests (Context Agent A2A discovery, send, polling, approval resume)
- `test_dispatch_a2a.py` — 1 test (Context Agent -> CLI Agent real A2A dispatch adapter)
- `test_cli_a2a_server.py` — 2 tests (CLI Agent A2A send, polling, legacy compatibility)

## Linting

```bash
# Check
uv run ruff check .

# Auto-fix
uv run ruff check --fix .

# Format
uv run ruff format .
```

## Verifying Data in Supabase

After running the workflow, you can inspect the data directly:

```sql
-- Recent runs with status
SELECT id, status, risk, assistant, created_at FROM runs ORDER BY created_at DESC LIMIT 5;

-- Prompts for a run
SELECT content, assistant FROM prompts WHERE run_id = '<run-id>';

-- Plan for a run
SELECT content, version FROM plans WHERE run_id = '<run-id>';

-- Approval decision for a run
SELECT decision, risk, reason, reviewer FROM approvals WHERE run_id = '<run-id>';

-- Context snapshot for a run
SELECT summary, sources FROM context_snapshots WHERE run_id = '<run-id>';

-- Durable issue memory saved for a run
SELECT title, source_type, metadata FROM documents
WHERE source_type = 'issue_memory'
  AND metadata->>'run_id' = '<run-id>';

-- Ingested documents
SELECT source_type, title, chunk_index, vector_id FROM documents ORDER BY created_at DESC;
```

These queries can be run via the Supabase MCP (`mcp__supabase__execute_sql`) or the Supabase dashboard.

## Pipeline Architecture Summary

```
User prompt
    │
    ▼
POST /tasks/send or JSON-RPC POST /a2a/contextsuite-context-agent
    │
    ▼
┌─────────┐   ┌──────────┐   ┌──────┐   ┌──────────┐   ┌─────────┐   ┌─────────┐
│ intake   │──▶│ retrieve  │──▶│ plan │──▶│ classify │──▶│ approve │──▶│ package │
│          │   │           │   │      │   │          │   │         │   │         │
│ Supabase │   │ Gemini    │   │Gemini│   │ regex    │   │ policy  │   │ build   │
│ create   │   │ Qdrant    │   │ 2.5  │   │ pattern  │   │ + risk  │   │ A2A     │
│ run      │   │ (Neo4j)   │   │ Flash│   │ matching │   │ check   │   │ payload │
└─────────┘   └──────────┘   └──────┘   └──────────┘   └─────────┘   └─────────┘
                                                              │
                                                         if rejected
                                                              │
                                                              ▼
                                                             END
```

## Troubleshooting

| Problem | Solution |
|---|---|
| `gemini-2.0-flash` 404 error | Model deprecated. Code uses `gemini-2.5-flash`. Update if model changes again. |
| Neo4j `DatabaseNotFound` | Known Aura provisioning issue. Graph queries are best-effort and skipped if Neo4j is down. See `KNOWN_ISSUES.md`. |
| `extra="ignore"` errors on startup | The `.env` file has variables not defined in the settings model. `extra="ignore"` in config.py handles this. |
| Empty retrieval results | Run `uv run python scripts/ingest_demo.py` to seed demo data. |
| Supabase connection refused | Check `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in `.env`. |
| Qdrant timeout | Check `QDRANT_URL` and `QDRANT_API_KEY` in `.env`. Free tier may sleep after inactivity. |

Neo4j status note:

- Aura connectivity is now expected to work when `NEO4J_URI` uses `neo4j+s://` and `NEO4J_DATABASE` matches the Aura database ID.
