# Running and Testing the Pipeline

This document explains how to run, test, and verify the ContextSuite pipeline.

## Prerequisites

1. **Python 3.12+** and **uv** installed
2. A `.env` file in the project root with all required variables (copy from `.env.example`)
3. Active cloud services: Supabase, Qdrant Cloud, Google AI (Gemini)

## Quick Start

```bash
# Install all dependencies
uv sync

# Run the full test suite (no cloud services needed)
uv run pytest -v

# Start the Context Agent server
uv run context-agent
# or directly:
uv run uvicorn contextsuite_agent.server:app --host 127.0.0.1 --port 8000
```

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

## Seeding Demo Data

The demo data represents a fictional `acme/payments` repository with incidents, ADRs, constraints, and code summaries.

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

Expected: `approval.approved: true`, `status: "ready"`, `task_id` is set.

### Send a high-risk prompt (should be rejected)

```bash
curl -X POST http://127.0.0.1:8000/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Delete all old payment records from the production database",
    "repository": "acme/payments",
    "assistant": "codex"
  }'
```

Expected: `approval.approved: false`, `risk.level: "high"`, `task_id: null`.

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
curl http://127.0.0.1:8000/.well-known/agent.json
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

Current test counts (42 total):
- `test_contracts.py` — 25 tests (A2A schemas, agent cards, types)
- `test_ingestion.py` — 9 tests (chunker, document sources)
- `test_workflow.py` — 8 tests (risk classification)

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

-- Ingested documents
SELECT source_type, title, chunk_index, vector_id FROM documents ORDER BY created_at DESC;
```

These queries can be run via the Supabase MCP (`mcp__supabase__execute_sql`) or the Supabase dashboard.

## Pipeline Architecture Summary

```
User prompt
    │
    ▼
POST /tasks/send
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
