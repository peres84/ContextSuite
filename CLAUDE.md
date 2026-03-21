# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What Is This

ContextSuite is a context, governance, and memory layer for AI coding workflows. A user sends a prompt to a Context Agent, which gathers project memory, checks constraints, reviews a plan, then forwards approved work over A2A to a Local Agent Client that runs a coding assistant CLI (Codex, Claude Code, or Cursor).

## Key Documents

- `AGENT.md` — agent-facing working brief with locked decisions and working rules
- `docs/plan.md` — **tracked** MVP execution checklist (read before implementation work)
- `docs/plan/CONTEXTSUITE_MVP_IMPLEMENTATION_ARCHITECTURE.md` — implementation architecture (git-ignored)
- `docs/plan/CONTEXTSUITE_EXTENDED_PLAN.md` — broader product context (git-ignored)

Always read `docs/plan.md` before starting implementation. Pick the next unchecked task from the current phase.

## Locked Architecture Decisions

Do not change these unless the user explicitly asks:

- **A2A-first**: A2A is the protocol between Context Agent and Local Agent Client
- **MCP is optional/internal** to the Context Agent only — never use it as the main transport
- **Cloud stack**: Supabase (relational), Qdrant Cloud (vector), Neo4j Aura (graph)
- **Embeddings**: Gemini Embedding 2 multimodal
- **Orchestration**: LangGraph
- **Language**: prefer TypeScript for new application code

## Build Priorities

1. Shared contracts and A2A message schemas
2. Context Agent skeleton and core workflow
3. Local Agent Client skeleton
4. One working coding assistant adapter (prefer depth over breadth)
5. Persistence and retrieval wiring
6. Demo UI or CLI
7. Additional adapters and polish

## MCP Servers

Supabase MCP is connected for database operations. Use `docs-langchain` MCP for LangChain/LangGraph docs and `google-docs` MCP for Gemini API guidance.

## Conventions

- Use `@/` path aliases in frontend code
- Keep A2A payloads and execution states as explicit typed contracts
- Update checkboxes in `docs/plan.md` when completing tasks
- Add discovered subtasks to `docs/plan.md` in the correct phase
- Do not replace managed cloud services with self-hosted alternatives
