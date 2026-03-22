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
