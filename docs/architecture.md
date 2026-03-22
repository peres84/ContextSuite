# Project Architecture

This document defines the folder structure and package layout for the ContextSuite monorepo.

## Monorepo Layout

```
heilbronn-hackathon/
├── packages/
│   ├── shared/                      # Shared contracts, types, and A2A schemas
│   │   ├── contextsuite_shared/
│   │   │   ├── __init__.py
│   │   │   ├── a2a/                 # A2A message schemas
│   │   │   │   ├── __init__.py
│   │   │   │   ├── task.py          # Task payload schema
│   │   │   │   ├── status.py        # Status update schema
│   │   │   │   ├── result.py        # Result payload schema
│   │   │   │   └── error.py         # Error payload schema
│   │   │   ├── agent_card/          # Agent Card definitions
│   │   │   │   ├── __init__.py
│   │   │   │   ├── context_agent.py
│   │   │   │   └── cli_agent.py
│   │   │   └── types/               # Common types shared across packages
│   │   │       ├── __init__.py
│   │   │       ├── approval.py      # Approval and risk-level types
│   │   │       ├── run.py           # Run and trace ID types
│   │   │       └── prompt.py        # Prompt and plan types
│   │   └── pyproject.toml
│   │
│   ├── context-agent/               # Context Agent — cloud-side orchestration
│   │   ├── contextsuite_agent/
│   │   │   ├── __init__.py
│   │   │   ├── server.py            # HTTP/A2A server (FastAPI)
│   │   │   ├── workflow/            # LangGraph workflow
│   │   │   │   ├── __init__.py
│   │   │   │   ├── graph.py         # Main LangGraph graph
│   │   │   │   ├── state.py         # Graph state definition
│   │   │   │   └── nodes/           # Individual workflow nodes
│   │   │   │       ├── __init__.py
│   │   │   │       ├── intake.py
│   │   │   │       ├── retrieve.py
│   │   │   │       ├── plan.py
│   │   │   │       ├── risk.py
│   │   │   │       ├── approve.py
│   │   │   │       └── dispatch.py
│   │   │   ├── retrieval/           # Context retrieval
│   │   │   │   ├── __init__.py
│   │   │   │   ├── vector.py        # Qdrant Cloud client
│   │   │   │   ├── graph.py         # Neo4j Aura client
│   │   │   │   └── ranking.py       # Result ranking across sources
│   │   │   ├── persistence/         # Supabase data access
│   │   │   │   ├── __init__.py
│   │   │   │   ├── runs.py
│   │   │   │   ├── approvals.py
│   │   │   │   └── prompts.py
│   │   │   ├── embeddings/          # Gemini Embedding 2 integration
│   │   │   │   └── __init__.py
│   │   │   └── config.py            # Environment config loader
│   │   └── pyproject.toml
│   │
│   └── cli-agent/                   # Local Agent Client — runs on dev machine
│       ├── contextsuite_cli/
│       │   ├── __init__.py
│       │   ├── server.py            # Local A2A listener
│       │   ├── executor/            # Task execution lifecycle
│       │   │   ├── __init__.py
│       │   │   ├── lifecycle.py     # State machine for task execution
│       │   │   └── stream.py        # Output streaming back to Context Agent
│       │   ├── adapters/            # Coding assistant CLI adapters
│       │   │   ├── __init__.py
│       │   │   ├── base.py          # Base adapter interface
│       │   │   ├── codex.py         # Codex CLI adapter
│       │   │   ├── claude.py        # Claude Code CLI adapter
│       │   │   └── cursor.py        # Cursor CLI adapter
│       │   ├── workspace/           # Workspace and repo targeting
│       │   │   └── __init__.py
│       │   └── config.py            # Local environment config
│       └── pyproject.toml
│
├── docs/
│   ├── architecture.md              # This file
│   ├── plan.md                      # MVP execution checklist
│   ├── workflow.png                 # Workflow diagram
│   └── plan/                        # Extended planning docs (git-ignored)
│
├── frontend/                        # Legacy demo app (not used for MVP)
├── media/                           # Branding assets
│
├── pyproject.toml                   # Root project config (uv workspace)
├── uv.lock                          # uv lockfile
├── .python-version                  # Python version pin
├── .env.example                     # Environment variable template
├── .gitignore
├── CLAUDE.md
├── AGENT.md
├── README.md
└── LICENSE
```

## Package Descriptions

### `packages/shared`

Shared contracts consumed by both the Context Agent and the CLI Agent. Uses Pydantic models for all schemas. Contains:

- A2A message schemas (task, status, result, error)
- Agent Card definitions
- Common types (approval, risk levels, run/trace IDs, prompts)

No runtime dependencies on cloud services.

### `packages/context-agent`

The cloud-side Context Agent. Receives user prompts, retrieves context, generates/reviews plans, classifies risk, routes approvals, and dispatches approved tasks over A2A to the CLI Agent.

Key dependencies:

- **LangGraph** for workflow orchestration
- **FastAPI** for the HTTP/A2A server
- **Supabase Python client** for relational persistence
- **Qdrant client** for vector retrieval
- **Neo4j Python driver** for graph relationships
- **Google GenAI SDK** for Gemini Embedding 2

### `packages/cli-agent`

The installable Local Agent Client that runs on the developer's machine. Receives A2A tasks from the Context Agent, selects and runs a coding assistant CLI, streams progress, and returns results.

Key dependencies:

- **FastAPI** for the local A2A listener
- Subprocess management for coding assistant CLIs (Codex, Claude Code, Cursor)

## Dependency Graph

```
shared ← context-agent
shared ← cli-agent
```

Both `context-agent` and `cli-agent` depend on `shared`. They do not depend on each other — they communicate exclusively over A2A at runtime.

## Tooling

- **uv** — package manager and workspace tool
- **Ruff** — linting and formatting
- **pytest** — testing
- **Python 3.12+**

## Naming Conventions

- Package import names use underscores: `contextsuite_shared`, `contextsuite_agent`, `contextsuite_cli`
- Source files use snake_case
- Pydantic models for all data contracts
- Each module has an `__init__.py` that re-exports the public API
