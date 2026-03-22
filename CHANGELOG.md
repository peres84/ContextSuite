# Changelog

All notable changes to ContextSuite are documented in this file.

## [0.1.0] - 2026-03-22

### Phase 1: Repository And Developer Setup

- Created Python/uv monorepo with three packages: `shared`, `context-agent`, `cli-agent`
- Added `pnpm-workspace.yaml` replaced by `pyproject.toml` with uv workspace config
- Added `.env.example` with all service variables (Supabase, Qdrant, Neo4j, Gemini, A2A)
- Added Ruff for linting and formatting, pytest for testing
- Added `uv run context-agent` and `uv run cli-agent` start commands
- Added `docs/architecture.md` defining full folder structure and package layout
- Updated README with local setup, prerequisites, and available commands
- Updated CLAUDE.md and AGENT.md to reflect Python stack and ignore frontend

### Phase 2: Shared Contracts And A2A Design

- Defined A2A-spec Agent Cards with provider, capabilities, skills, and interfaces
- Built Context Agent card (5 skills) and CLI Agent card (3 skills)
- Defined `Task` model with `TaskState` enum (7 states: working, completed, failed, canceled, rejected, input_required, auth_required)
- Defined `Message` with `Part` types: `TextPart`, `FilePart`, `DataPart`
- Defined `Artifact` model for output capture
- Defined `TaskPayload` as ContextSuite-specific extension (carried as DataPart)
- Defined `TaskStatusUpdate` with progress tracking (0.0-1.0)
- Defined `TaskResult` with artifacts and duration
- Defined `TaskError` with 8 error codes (execution_failed, adapter_not_found, workspace_not_found, timeout, cancelled, policy_blocked, approval_denied, internal_error)
- Defined `RiskLevel` (low/medium/high), `RiskSignal`, `RiskAssessment`
- Defined `ApprovalDecision` with reviewer, policy violations, timestamps
- Defined `RunMeta` with auto-generated `run_id` and `trace_id` on all messages
- Added 25 contract validation tests (all passing)

### Phase 3: Cloud Infrastructure Bootstrap

- Validated Supabase connectivity (connected, no tables yet)
- Validated Qdrant Cloud connectivity (connected, no collections yet)
- Validated Gemini Embedding 2 multimodal (3072-dim vectors working)
- Neo4j Aura instance created — connects via `bolt+s://` but has database provisioning issue (see KNOWN_ISSUES.md)
- Created `scripts/` directory with connectivity test scripts for all services
- Created `scripts/test_all.py` runner to test everything at once

### Phase 4: Data Model And Persistence

- Designed and applied Supabase migration: 7 tables (`repositories`, `runs`, `prompts`, `plans`, `context_snapshots`, `approvals`, `outcomes`), 3 enums, indexes, auto-update triggers
- Created Qdrant `contextsuite` collection (3072-dim, cosine similarity) for Gemini Embedding 2
- Designed Neo4j graph model: 6 node labels, 10 relationship types, uniqueness constraints, indexes
- Documented data ownership rules in `docs/architecture.md` (Supabase authoritative, Qdrant/Neo4j derived)
- Implemented persistence layer: `RunsRepo`, `PromptsRepo`, `ApprovalsRepo` with full CRUD
- Implemented retrieval layer: Qdrant vector search, Neo4j graph queries, cross-source ranking
- Implemented Gemini Embedding 2 client: `embed_text()` / `embed_texts()`
- Seeded demo data: 1 repository + 5 context documents (incidents, ADRs, constraints) embedded in Qdrant
- Verified semantic search: "webhook crashes with null email" → 0.80 similarity to correct incident
- Documented all schemas in `docs/schemas/` (supabase.md, qdrant.md, neo4j.md) for recovery

### Phase 5: Context Ingestion And Retrieval

- Defined input source types: `incident`, `adr`, `constraint`, `doc`, `code_summary`, `issue`
- Implemented document chunker with paragraph/sentence boundary splitting and configurable overlap
- Built ingestion pipeline: chunk → embed (Gemini 2) → store in Qdrant → track in Supabase
- Added `documents` table in Supabase for ingestion metadata tracking (source_type, vector_id, chunks)
- Added `DocumentsRepo` for querying ingested documents by repository, source type, or vector ID
- Built `retrieve_context()` high-level function combining vector search + graph queries + ranking
- Created `scripts/ingest_demo.py` — ingests 6 demo documents through the full pipeline
- Verified end-to-end: "webhook crashes when customer email is null" → 0.81 similarity to correct incident
- Added 9 unit tests for chunker and document sources (34 total tests passing)
- Neo4j graph seeding still blocked by Aura provisioning issue (see KNOWN_ISSUES.md)

### Phase 6: Context Agent Core Workflow

- Built LangGraph workflow: intake → retrieve → plan → classify → approve → package
- Implemented prompt intake node: creates run, persists prompt, resolves repository
- Implemented context retrieval node: embeds prompt, searches Qdrant, saves context snapshot
- Implemented plan generation node: Gemini 2.5 Flash generates task plans from prompt + context
- Implemented risk classification node: regex-based signal detection with weighted scoring
- Implemented approval routing: auto-approve low/medium risk, reject high risk, policy blocklist
- Implemented task packaging node: builds A2A `TaskPayload` for dispatch to CLI Agent
- Added `POST /tasks/send` endpoint to the Context Agent server
- Added structured logging across all workflow nodes
- Verified end-to-end: low-risk prompt → auto-approved with plan and task_id
- Verified end-to-end: high-risk prompt → 3 signals detected, rejected with reason
- Added 8 risk classification unit tests (42 total tests passing)

### Phase 7: Local Agent Client

- Built `POST /tasks/receive` endpoint on the CLI Agent for A2A task receipt
- Implemented adapter registry with auto-registration of all adapters on import
- Implemented task execution lifecycle with timeout (300s) and error handling
- Health endpoint now reports registered adapters
- Added A2A dispatch node to Context Agent workflow (package → dispatch → END)
- Context Agent now calls CLI Agent over HTTP and persists outcome in Supabase

### Phase 8: Coding Assistant Adapters

- Implemented Codex CLI adapter (`codex --quiet --auto-edit --prompt`)
- Implemented Claude Code CLI adapter (`claude --print --dangerously-skip-permissions --prompt`)
- Implemented Cursor CLI adapter (`cursor --prompt`)
- All adapters: subprocess execution, stdout/stderr capture, artifact collection
- All adapters return `TaskResult` (completed/failed) with normalized output
- Missing CLI tools are reported as `TaskResult(state=failed)` with install instructions

### Phase 9: Approval And Safety Layer

- Risk classification and approval routing remain in the main workflow
- Policy blocklist: `drop database`, `rm -rf /`, `delete all users`, `disable authentication`
- High-risk tasks now escalate to human approval instead of being hard-rejected immediately
- Added approval status contract with `approved`, `rejected`, and `escalated`
- Added `POST /tasks/{run_id}/approval` to resolve human approvals and resume the persisted run
- Approval history now records both escalation and final human decisions in Supabase

### Phase 10: CLI Demo Surface And Saved Memory

- Built `contextsuite` CLI app (`packages/cli-app`) with Click + Rich + prompt-toolkit
- Interactive terminal chat with prompt history (`.contextsuite/history.txt`)
- `contextsuite init` — initialize project folder with `.contextsuite.json` config
- `contextsuite chat` — interactive mode or one-shot prompt via arguments
- `contextsuite status` — show current project configuration
- File references via `@file.py` tags — attaches file content to the prompt
- Image attachments via `#image:path.png` or `/image path.png` commands
- Assistant selection via `/assistant codex|claude|cursor` during session
- Rich output: colored risk levels, approval status, plan panels, execution results, and saved memory
- Sends prompts to Context Agent `POST /tasks/send` with full attachment support
- CLI now prompts the operator for approval when a run is escalated
- Added post-dispatch `save_memory` workflow step
- Issue-related outcomes now persist as durable `issue_memory` documents for future retrieval
- Memory saving falls back to plain Supabase document storage if vector ingestion fails

### Documentation Refresh

- Updated root `README.md` to reflect the human approval flow
- Rewrote `docs/workflow.md` for the current workflow, approval endpoint, and saved memory behavior
- Updated `docs/pipeline.md` with escalated approval testing and issue-memory verification queries
- Refreshed `docs/demo-script.md` so the live story matches the current approval pause behavior
- Added `docs/README.md` as a docs index for operators and judges

### Full A2A E2E Verified

- Context Agent → CLI Agent round-trip working over HTTP
- Low-risk prompt: approved → dispatched → codex adapter executed → result returned
- Outcome (success/failure) persisted in Supabase `outcomes` table
