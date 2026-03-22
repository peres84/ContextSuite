# Documentation Index

This folder collects the main operator, demo, and architecture docs for ContextSuite.

## Start Here

- [../README.md](../README.md) - project overview, setup, and commands
- [workflow.md](workflow.md) - end-to-end workflow, approval states, and saved memory behavior
- [pipeline.md](pipeline.md) - how to run, test, and verify the pipeline
- [demo-script.md](demo-script.md) - short live demo script
- [user-guideline.md](user-guideline.md) - step-by-step operator guide

## Architecture And Data

- [architecture.md](architecture.md) - monorepo layout and package responsibilities
- [schemas/supabase.md](schemas/supabase.md) - Supabase tables and enums
- [schemas/qdrant.md](schemas/qdrant.md) - Qdrant collection design
- [schemas/neo4j.md](schemas/neo4j.md) - Neo4j graph model

## Planning

- [plan.md](plan.md) - MVP checklist with current phase status
- [plan/](plan/) - pitch, mockups, and planning artifacts

## Current Workflow Highlights

- High-risk tasks now pause for human approval instead of being dispatched automatically.
- Human approvals are resolved through the Context Agent API and can resume the same persisted run.
- Issue-related outcomes are saved as durable `issue_memory` for future retrieval.
