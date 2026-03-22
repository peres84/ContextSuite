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
- Defined `TaskError` with 8 error codes (`execution_failed`, `adapter_not_found`, `workspace_not_found`, `timeout`, `cancelled`, `policy_blocked`, `approval_denied`, `internal_error`)
- Defined `RiskLevel` (`low`/`medium`/`high`), `RiskSignal`, `RiskAssessment`
- Defined `ApprovalDecision` with reviewer, policy violations, timestamps
- Defined `RunMeta` with auto-generated `run_id` and `trace_id` on all messages
- Added 25 contract validation tests (all passing)

### Phase 3: Cloud Infrastructure Bootstrap

- Validated Supabase connectivity (connected, no tables yet)
- Validated Qdrant Cloud connectivity (connected, no collections yet)
- Validated Gemini Embedding 2 multimodal (3072-dim vectors working)
- Neo4j Aura instance created and later fixed (see KNOWN_ISSUES.md)
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
- Seeded demo data: 1 repository plus 5 context documents (incidents, ADRs, constraints) embedded in Qdrant
- Verified semantic search: "webhook crashes with null email" maps to the correct incident
- Documented all schemas in `docs/schemas/` (`supabase.md`, `qdrant.md`, `neo4j.md`)

### Phase 5: Context Ingestion And Retrieval

- Defined input source types: `incident`, `adr`, `constraint`, `doc`, `code_summary`, `issue`
- Implemented document chunker with paragraph/sentence boundary splitting and configurable overlap
- Built ingestion pipeline: chunk -> embed (Gemini 2) -> store in Qdrant -> track in Supabase
- Added `documents` table in Supabase for ingestion metadata tracking (`source_type`, `vector_id`, chunks)
- Added `DocumentsRepo` for querying ingested documents by repository, source type, or vector ID
- Built `retrieve_context()` high-level function combining vector search, graph queries, and ranking
- Created `scripts/ingest_demo.py` to ingest 6 demo documents through the full pipeline
- Verified end-to-end retrieval for the null-email webhook scenario
- Added 9 unit tests for chunker and document sources

### Phase 6: Context Agent Core Workflow

- Built LangGraph workflow: intake -> retrieve -> plan -> classify -> approve -> package
- Implemented prompt intake node: creates run, persists prompt, resolves repository
- Implemented context retrieval node: embeds prompt, searches Qdrant, saves context snapshot
- Implemented plan generation node: Gemini 2.5 Flash generates task plans from prompt plus context
- Implemented risk classification node: regex-based signal detection with weighted scoring
- Implemented approval routing: auto-approve low/medium risk, reject high-risk policy violations, escalate high risk
- Implemented task packaging node: builds A2A `TaskPayload` for dispatch to CLI Agent
- Added `POST /tasks/send` endpoint to the Context Agent server
- Added structured logging across all workflow nodes
- Verified end-to-end low-risk prompt flow and high-risk escalation flow
- Added 8 risk-classification unit tests

### Phase 7: Local Agent Client

- Built `POST /tasks/receive` endpoint on the CLI Agent for task receipt
- Implemented adapter registry with auto-registration of all adapters on import
- Implemented task execution lifecycle with timeout (300s) and error handling
- Health endpoint now reports registered adapters
- Added A2A dispatch node to Context Agent workflow (`package` -> `dispatch` -> `END`)
- Context Agent now calls CLI Agent over HTTP and persists outcomes in Supabase

### Phase 8: Coding Assistant Adapters

- Implemented Codex CLI adapter (`codex --quiet --auto-edit --prompt`)
- Implemented Claude Code CLI adapter (`claude --print --dangerously-skip-permissions --prompt`)
- Implemented Cursor CLI adapter (`cursor --prompt`)
- All adapters now perform subprocess execution, stdout/stderr capture, and artifact collection
- All adapters return normalized `TaskResult`
- Missing CLI tools are reported with install instructions instead of crashing the workflow

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
- Added `contextsuite init`, `contextsuite chat`, and `contextsuite status`
- Added file references via `@file.py`
- Added image attachments via `#image:path.png` and `/image path.png`
- Added assistant switching via `/assistant codex|claude|cursor`
- Added rich output for risk, approval, plan, execution, and saved memory
- CLI now prompts the operator for approval when a run is escalated
- Added post-dispatch `save_memory` workflow step
- Issue-related outcomes now persist as durable `issue_memory` documents for future retrieval
- Memory saving falls back to plain Supabase document storage if vector ingestion fails

### Documentation Refresh

- Updated root `README.md` to reflect the human approval flow
- Rewrote `docs/workflow.md` for the current workflow, approval endpoint, and saved memory behavior
- Updated `docs/pipeline.md` with escalated approval testing and issue-memory verification queries
- Refreshed `docs/demo-script.md` so the live story matches the approval pause behavior
- Added `docs/README.md` as a docs index for operators and judges

### Phase 11: Demo Data And Storytelling

- Updated `scripts/demo_scenarios.py` to cover approved, escalated-approved, escalated-rejected, policy-blocked, and medium-risk flows
- Added JSON export support for captured demo transcripts
- Refreshed `docs/user-guideline.md` to match the real human approval and saved-memory flow
- Added `docs/fallback/README.md` with fallback capture instructions for demo backups

### Phase 12: Real A2A Protocol Compatibility

- Replaced the old A2A-shaped task/message models with protocol-aligned A2A schemas:
  - `Task.kind`, `history`, `contextId`, and `status.message`
  - `Message.messageId`, `taskId`, `contextId`, and `kind`
  - `TextPart`, `FilePart`, and `DataPart` now use `kind`
- Rebuilt Agent Cards around the real A2A shape:
  - `protocolVersion`
  - `url`
  - `preferredTransport`
  - `additionalInterfaces`
  - `defaultInputModes` / `defaultOutputModes`
- Added shared JSON-RPC/A2A request models for `message/send` and `tasks/get`
- Added Context Agent A2A discovery routes:
  - `GET /.well-known/agent-card.json`
  - `GET /.well-known/agent.json` (legacy alias)
  - `GET /a2a/{assistant_id}/.well-known/agent-card.json`
- Added Context Agent A2A endpoint at `POST /a2a/contextsuite-context-agent`
- Implemented JSON-RPC `message/send` on the Context Agent as a thin adapter over the existing workflow
- Implemented JSON-RPC `tasks/get` on the Context Agent backed by persisted runs, approvals, prompts, and outcomes
- Implemented A2A approval continuation on the Context Agent by reusing the existing human-approval resume logic
- Added CLI Agent A2A discovery routes and `POST /a2a/contextsuite-cli-agent`
- Implemented CLI Agent JSON-RPC `message/send` as a thin adapter over the existing execution lifecycle
- Implemented CLI Agent `tasks/get` backed by in-memory task snapshots for the current process
- Updated Context Agent dispatch to prefer real A2A JSON-RPC to the CLI Agent and safely fall back to `/tasks/receive`
- Preserved the legacy working endpoints:
  - Context Agent: `/tasks/send`, `/tasks/{run_id}/approval`
  - CLI Agent: `/tasks/receive`
- Added 7 new A2A server/dispatch tests and expanded shared contract coverage
- Verified the full Python test suite: 56 passing tests

### Remaining A2A Gaps

- `message/stream` is not implemented yet
- Push notifications are not implemented
- Non-blocking/background A2A execution is not implemented yet
- CLI Agent `tasks/get` is in-memory only

### Full A2A E2E Verified

- Context Agent -> CLI Agent round-trip working over HTTP
- Low-risk prompt: approved -> dispatched -> codex adapter executed -> result returned
- Outcome (success/failure) persisted in Supabase `outcomes` table

### Phase 13: Green-Brand Constraint Demo And Retrieval Hardening

- Added a new `demo/` React + Vite website to demonstrate a must-not-break brand rule
- Added demo memory documents for `demo/green-brand-site`:
  - brand constraint: the primary color must remain green
  - prior incident: a red redesign was rejected
  - theme-system notes pointing to the CSS variables used by the site
- Added `scripts/ingest_brand_demo.py` to ingest the green-brand demo through the normal pipeline
- Made both demo ingestion scripts idempotent by clearing prior demo document chunks before re-ingest:
  - `scripts/ingest_brand_demo.py`
  - `scripts/ingest_demo.py`
- Hardened Qdrant retrieval by:
  - scoping vector retrieval by `repository_id`
  - auto-creating the `repository_id` payload index when repo-scoped retrieval is used
- Added a narrow constraint-conflict rule in risk classification:
  - if retrieved context says the primary brand color must remain green
  - and the user asks to change the primary styling to another color like red
  - the run is classified as high risk and escalated before execution
- Added workflow tests for:
  - brand-constraint conflict detection
  - avoiding false positives when the plan merely repeats the warning
- Added `docs/green-guard-demo.md` with a dedicated runbook for the new demo
- Linked the new runbook from `docs/README.md`
- Verified live behavior:
  - the red-theme prompt is retrieved correctly
  - risk becomes `high`
  - approval becomes `escalated`
  - execution is paused before dispatch

### Phase 14: Windows CLI Runtime Hardening And Demo Verification

- Updated the CLI-agent adapters to use a Windows-safe subprocess path backed by worker threads instead of `asyncio.create_subprocess_exec(...)`
- Updated the Codex adapter to the current `codex exec --full-auto --output-last-message ...` command shape
- Added regression coverage for the Codex adapter command path and result parsing
- Changed both packaged agent entrypoints so `uv run context-agent` and `uv run cli-agent` default to `reload = false`
- Verified the full approval-resume path on clean temporary ports:
  - red-theme request -> escalated approval
  - human approval -> CLI dispatch
  - Codex completion returned to the Context Agent
- Documented the operational caveat that a stale listener on port `8001` can shadow the new CLI Agent and make the demo appear broken
- Captured a live demo-site refresh in:
  - `demo/src/App.jsx`
  - `demo/src/styles.css`
  The refresh keeps the required green theme while tightening the hero, feature, and principles sections for the green-brand demo

### Phase 15: Demo Launcher, Claude CLI Compatibility, And Clearer Agent UX

- Updated the Claude Code adapter to match the current CLI contract by using `claude --print ...` with the prompt passed positionally instead of the removed `--prompt` flag
- Added regression coverage for the Claude adapter command path and subprocess integration
- Propagated `workspace_path` from the `contextsuite` CLI through the Context Agent and A2A packaging layer so the CLI Agent executes in the selected project directory instead of falling back to `.`
- Added compact shared service logging in `packages/shared/contextsuite_shared/logutils.py`
- Added request start/finish timing to both HTTP servers and clearer dispatch timing around the blocking Context Agent -> CLI Agent handoff
- Added periodic subprocess heartbeat logs while Codex, Claude Code, or Cursor are still running so long executions no longer look like silent hangs
- Added `scripts/start_demo_agents.ps1` to:
  - stop stale agent processes
  - free common demo ports
  - open fresh Context Agent, CLI Agent, and demo prompt terminals
  - optionally launch the demo site
- Updated `docs/green-guard-demo.md` with the one-click launcher flow
- Improved the `contextsuite` CLI output so the user can distinguish:
  - what came from the Context Agent
  - what came from the coder agent
  - the handoff between review, approval, dispatch, and execution
- Added an `Agent Interaction` panel to the CLI result view so the workflow is visible as a short timeline instead of only separate plan and execution panels
