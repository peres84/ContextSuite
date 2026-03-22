# AGENT.md

This file is the agent-focused working brief for this repository.

Use it together with the human-facing README. When working in this repo, use `docs/plan.md` as the tracked execution checklist for the MVP.

## Project Overview

ContextSuite is a context, governance, and memory layer for AI coding workflows.

The MVP goal is to prove this end-to-end flow:

1. A user sends a prompt to the Context Agent.
2. The Context Agent retrieves relevant memory, constraints, and prior incidents.
3. The Context Agent generates or reviews a plan and applies risk checks.
4. Approved work is sent over A2A to the ContextSuite Local Agent Client.
5. The Local Agent Client runs a coding assistant CLI such as Codex, Claude Code, or Cursor.
6. The result, approvals, and useful memory are stored for future runs.

## Source Of Truth

Read these documents before making significant implementation changes:

- `README.md`: human-facing project summary and workflow image
- `docs/plan.md`: tracked MVP execution checklist and phase plan
- `docs/plan/CONTEXTSUITE_MVP_IMPLEMENTATION_ARCHITECTURE.md`: deeper implementation architecture
- `docs/plan/CONTEXTSUITE_EXTENDED_PLAN.md`: broader product and system context

Important note:

- `docs/plan.md` is tracked and should be used as the execution checklist
- `docs/plan/` contains useful reference material, but that folder is git-ignored in this repo

## Locked MVP Decisions

These are current architecture constraints and should not be changed unless the user explicitly asks:

- Use an A2A-first architecture
- The boundary between ContextSuite and the coding executor is A2A
- The installable bridge is the ContextSuite Local Agent Client
- The Local Agent Client controls local coding assistant CLIs
- MCP is optional and internal to the Context Agent only
- Do not use MCP as the main transport between ContextSuite and the coding executor
- Use Gemini Embedding 2 multimodal for embeddings
- Use Supabase as the relational system of record
- Use Qdrant Cloud for vector retrieval
- Use Neo4j Aura for graph relationships
- Keep the MVP simple and demo-first
- The final MVP should use real A2A messaging, not a fake placeholder flow

## Connected MCP Capabilities (Project Context)

The following MCP tools are connected for this project context:

- Supabase: connected
- docs-langchain: connected
- google-docs: connected

How agents should use this:

- Use Supabase MCP directly for database operations such as creating tables, updating schema objects, and validating relational structure for MVP data models.
- Use docs-langchain MCP to find relevant LangChain/LangGraph documentation for implementation details and API usage.
- Use google-docs MCP to find relevant Google Gemini documentation and model/API guidance when implementing Gemini-based features.

## Default Build Priorities

Unless the user redirects the work, follow this order:

1. Shared contracts and A2A message schemas
2. Context Agent skeleton and core workflow
3. Local Agent Client skeleton
4. One working coding assistant adapter
5. Persistence and retrieval wiring
6. Thin demo UI or CLI
7. Additional adapters and polish

For the first vertical slice, prefer one working adapter over partial support for many adapters.

## Repository Layout

- `README.md`: human-facing overview
- `AGENT.md`: agent-facing guidance for this repo
- `docs/plan.md`: tracked MVP build checklist
- `docs/workflow.png`: workflow diagram used in the README
- `docs/plan/`: deeper planning and architecture references
- `frontend/`: existing Next.js frontend app
- `media/`: branding assets and favicons

## Frontend Notes (Demo should wait for user request, should be ignored)

There is already a frontend app in `frontend/` built with Next.js and React.

Known commands inside `frontend/`:

- Install dependencies: `pnpm install`
- Start dev server: `pnpm dev`
- Build: `pnpm build`
- Lint: `pnpm lint`

If you change frontend code, use the `frontend/` app rather than creating a second frontend unless the user asks for a new structure.

## Working Rules For Agents

- Read `docs/plan.md` before starting implementation work
- Pick tasks from the current phase or the recommended vertical slice
- Keep changes aligned with the locked MVP decisions above
- Prefer simple, working paths over generalized infrastructure
- When you complete a meaningful task, update the relevant checkbox in `docs/plan.md`
- If you discover a missing subtask, add it to `docs/plan.md` in the correct phase
- If you materially change architecture or scope, update both the relevant docs and `docs/plan.md`
- Avoid editing ignored planning docs unless the user asks for those docs specifically
- Do not replace the managed cloud services with self-hosted alternatives unless the user asks
- Do not shift the main ContextSuite-to-executor communication to MCP

## Code Style And Conventions

- Use Python for all backend and agent code
- Use Pydantic models for all data contracts and A2A schemas
- Use Ruff for linting and formatting
- Preserve the local style of the file you edit
- Keep modules focused and composable
- Prefer explicit contracts for A2A payloads and execution states
- Keep demo copy and UX simple and easy to follow
- `frontend/` is a legacy demo app — do not modify it

## Testing And Validation

- Run `uv run ruff check .` for linting
- Run `uv run pytest` for tests
- For contract-heavy code, add schema validation tests early
- Do not claim tests passed unless you actually ran them

## MVP Definition Of Done

The MVP is done when all of the following are true:

- One prompt can move through the full system from intake to stored result
- The Context Agent retrieves context before execution
- The Context Agent performs plan review or plan generation with risk handling
- A real A2A task is sent to the Local Agent Client
- At least one coding assistant adapter works end to end
- Results and memory are persisted in the selected data stores
- The demo clearly shows why this is better than direct-to-agent prompting

## If You Are Unsure What To Do Next

Start by opening `docs/plan.md` and continue the next unchecked task that helps complete the first end-to-end vertical slice.
