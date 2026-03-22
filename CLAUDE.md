# CLAUDE.md

This file provides repository guidance for Claude Code and similar coding agents.

## What This Repo Is

ContextSuite is a context, governance, and memory layer for AI coding workflows.

Today the product supports:

- legacy HTTP for the current CLI and demo flow
- real A2A JSON-RPC for interoperable agent-to-agent calls
- A2A-first Context Agent to CLI Agent dispatch with legacy fallback

## Read These First

- `README.md`
- `docs/workflow.md`
- `docs/pipeline.md`
- `docs/user-guideline.md`
- `docs/architecture.md`
- `KNOWN_ISSUES.md`
- `docs/plan.md`

## Current Architectural Rules

Do not change these unless the user explicitly asks:

- A2A JSON-RPC is the primary agent-to-agent interface.
- Legacy HTTP routes remain for compatibility.
- Keep business logic in the existing workflow and use protocol adapters for compatibility work.
- MCP is optional/internal only, not the main transport to the executor.
- Supabase, Qdrant Cloud, and Neo4j Aura remain the selected stores.
- Gemini Embedding 2 remains the embedding model.
- Backend and agent code stays Python-first.

## A2A Reality Check

Implemented:

- agent card discovery
- `/a2a/{assistant_id}`
- `message/send`
- `tasks/get`
- approval continuation over A2A

Not implemented:

- `message/stream`
- push notifications
- background async A2A execution

## Working Conventions

- Preserve approvals, memory saving, and adapter behavior.
- When protocol and local types disagree, align to the real wire protocol.
- Update docs and tests with any route or contract change.
- Remember that `-p` points to a local execution workspace, while `-r` is only repository metadata unless that repository was ingested.
- Do not modify `frontend/` unless the user explicitly asks for frontend work.
