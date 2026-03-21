# ContextSuite

ContextSuite is an AI governance and memory layer for coding assistants.

It helps teams prevent repeated regressions by routing prompts through a Context Agent that reviews plans against historical issues, constraints, approvals, and risk policies before execution.

## Current Repository Scope

This repository is intentionally document-focused for the hackathon stage.

Tracked content is centered on planning documents in:

- `docs/plan/`

## Core Idea

For existing projects, prompts go to the Context Agent first.

1. Context Agent retrieves issue history and constraints.
2. Code agent submits a structured implementation plan.
3. Context Agent reviews risk and policy compliance.
4. Approval is automatic for low-risk or delegated to humans for medium/high-risk.
5. Code execution is allowed only after approval.
6. Indexing happens only for issue-related outcomes.

## Architecture Snapshot

- Orchestration: LangGraph
- Agent boundary: A2A
- Model and embeddings: Gemini + Gemini Embedding 2 multimodal
- Vector retrieval: Qdrant Cloud
- Audit/system of record: Supabase
- Relationship reasoning: Neo4j Aura

## Why This Matters

Most AI coding workflows are fast but context-fragile across long sessions.
ContextSuite preserves the "why" behind past fixes, reduces repeated incidents, and improves trust in AI-assisted changes.

## Main Planning Document

Use the extended plan here:

- `docs/plan/CONTEXTSUITE_EXTENDED_PLAN.md`

## Status

Hackathon MVP planning in progress.

Focus order:

1. End-to-end Context Agent workflow demo.
2. Issue-driven indexing correctness.
3. Approval and policy behavior.
4. Optional provider-facing onboarding UX.
