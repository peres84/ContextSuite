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
- Neo4j Aura instance created (connectivity pending instance resume)
- Created `scripts/` directory with connectivity test scripts for all services
- Created `scripts/test_all.py` runner to test everything at once
