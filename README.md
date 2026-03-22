# ContextSuite

<p align="center">
  <img src="media/logotype.png" alt="ContextSuite logotype" width="520" />
</p>

<p align="center">
  <strong>Context, governance, and memory for AI coding workflows</strong>
</p>

<p align="center">
  <a href="#license"><img src="https://img.shields.io/badge/License-MIT-16a34a?style=for-the-badge" alt="MIT License" /></a>
  <a href="#workflow"><img src="https://img.shields.io/badge/Workflow-A2A%20First-2563eb?style=for-the-badge" alt="A2A First Workflow" /></a>
  <a href="#mvp-goal"><img src="https://img.shields.io/badge/Status-Hackathon%20MVP-f59e0b?style=for-the-badge" alt="Hackathon MVP" /></a>
  <a href="#architecture-snapshot"><img src="https://img.shields.io/badge/Orchestration-LangGraph-111827?style=for-the-badge" alt="LangGraph Orchestration" /></a>
</p>

ContextSuite is a context, governance, and memory layer for AI coding workflows.

Instead of sending prompts directly to a coding assistant, the user sends them to a Context Agent first. The Context Agent gathers project memory, checks constraints and prior incidents, reviews the plan, and only then hands execution to a coding assistant through a simple A2A-based local bridge.

<p align="center">
  <img src="https://img.shields.io/badge/context-memory-0f766e?style=flat-square" alt="Context memory" />
  <img src="https://img.shields.io/badge/risk-reviewed-7c3aed?style=flat-square" alt="Risk reviewed" />
  <img src="https://img.shields.io/badge/local-agent%20client-enabled-1d4ed8?style=flat-square" alt="Local Agent Client enabled" />
  <img src="https://img.shields.io/badge/agentic-ai-334155?style=flat-square" alt="Agentic AI" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Gemini_Embedding_2-Multimodal-4285F4?style=flat-square&logo=google&logoColor=white" alt="Gemini Embedding 2 Multimodal" />
  <img src="https://img.shields.io/badge/Supabase-Managed_Postgres-3ECF8E?style=flat-square&logo=supabase&logoColor=white" alt="Supabase" />
  <img src="https://img.shields.io/badge/Qdrant-Cloud-FF6B6B?style=flat-square" alt="Qdrant Cloud" />
  <img src="https://img.shields.io/badge/Neo4j-Aura-0A66C2?style=flat-square&logo=neo4j&logoColor=white" alt="Neo4j Aura" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Coding_Agents-Codex%20%7C%20Claude%20Code%20%7C%20Cursor-4b5563?style=flat-square" alt="Supported coding agents" />
</p>

## What Works Today

- Context Agent workflow: intake -> retrieve -> plan -> classify -> approve -> package -> dispatch
- A2A handoff to a local CLI Agent over HTTP
- Adapter support for `codex`, `claude`, and `cursor`
- Context retrieval from Supabase, Qdrant Cloud, and Neo4j Aura
- Interactive terminal app via `contextsuite`
- Demo repository and scenarios for `acme/payments`

## MVP Notes

- Low-risk tasks are auto-approved.
- Medium-risk tasks are also auto-approved in MVP mode.
- High-risk tasks are rejected and not dispatched.
- File references are wired end to end.
- Image attachment syntax exists in the CLI, but the current workflow is still text-first. Treat image support as experimental.

## Workflow

![ContextSuite workflow](docs/workflow.png)

## Why It Exists

AI coding tools are fast, but they often lose important project context over time. Teams repeat bugs, miss constraints, and forget why past decisions were made. ContextSuite keeps that memory available at the moment a change is requested.

## MVP Goal

Build a demo where a user sends a prompt to ContextSuite, ContextSuite reviews the task, then forwards an approved job over A2A to a Local Agent Client that runs Codex, Claude Code, or Cursor CLI and returns the result.

## Architecture Snapshot

- Orchestration: LangGraph
- Agent-to-agent communication: A2A
- Local execution bridge: ContextSuite Local Agent Client
- Coding assistants for MVP: Codex CLI, Claude Code CLI, Cursor CLI
- Model and embeddings: Gemini + Gemini Embedding 2 multimodal
- Relational system of record: Supabase
- Vector retrieval: Qdrant Cloud
- Relationship graph: Neo4j Aura

## Project Structure

```
packages/
  shared/              Shared A2A contracts, agent cards, and types (Pydantic)
  context-agent/       Context Agent — LangGraph workflow, retrieval, persistence
  cli-agent/           CLI Agent — local client that runs coding assistant CLIs
  cli-app/             Interactive terminal client (`contextsuite`)
scripts/               Connectivity checks, seeding, and demo helpers
docs/
  architecture.md      Monorepo layout and package roles
  pipeline.md          Runtime and testing guide
  workflow.md          Workflow and API behavior
  user-guideline.md    End-to-end test instructions for humans
  plan.md              MVP execution checklist
```

See [`docs/architecture.md`](docs/architecture.md) for the complete folder tree.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Access to Supabase, Qdrant Cloud, Neo4j Aura, and Google Gemini
- At least one supported assistant CLI installed on `PATH`

Assistant CLI examples:

- Codex: `npm install -g @openai/codex`
- Claude Code: `npm install -g @anthropic-ai/claude-code`
- Cursor: make sure the `cursor` command is available on `PATH`

## Local Setup

Copy `.env.example` to `.env` and fill in your values before starting.

PowerShell:

```powershell
Copy-Item .env.example .env
```

Important Neo4j note:

- `NEO4J_URI` should use `neo4j+s://`
- `NEO4J_DATABASE` must be the Aura database ID, not always `neo4j`

```bash
# Clone and enter the repo
git clone <repo-url> && cd heilbronn-hackathon

# Copy env template and fill in your values
cp .env.example .env

# Install all dependencies
uv sync --all-packages

# Start the Context Agent (port 8000)
uv run context-agent

# Start the CLI Agent (port 8001) — in a second terminal
uv run cli-agent
```

Then seed the demo data and initialize a local demo workspace:

```bash
uv run pytest -q
uv run python scripts/ingest_demo.py
uv run python scripts/setup_neo4j.py
uv run python scripts/seed_neo4j.py
uv run python scripts/test_services.py
uv run contextsuite -p ./demo-project init -r "acme/payments" -a codex
uv run contextsuite -p ./demo-project chat
```

## Available Commands

| Command | Description |
|---|---|
| `uv run context-agent` | Start the Context Agent server |
| `uv run cli-agent` | Start the CLI Agent server |
| `uv run contextsuite -p ./demo-project chat` | Start the interactive CLI |
| `uv run python scripts/test_all.py` | Check Supabase, Qdrant, Neo4j, and Gemini |
| `uv run python scripts/test_services.py` | Check the local HTTP services |
| `uv run python scripts/demo_scenarios.py` | Run canned approved and blocked demo flows |
| `uv run ruff check .` | Lint the repo |
| `uv run ruff format .` | Format the repo |
| `uv run pytest -q` | Run tests |

## Near-Term Outcome

Prove a simple end-to-end flow:

- one prompt in
- one reviewed plan
- one approved A2A task
- one coding assistant execution
- one stored memory trail

## Documentation

- [User guideline](docs/user-guideline.md)
- [Pipeline guide](docs/pipeline.md)
- [Workflow guide](docs/workflow.md)
- [Architecture](docs/architecture.md)
- [Live demo script](docs/demo-script.md)

## Troubleshooting

- `uv run pytest` works but cloud scripts fail: check `.env` and service credentials.
- Neo4j connection fails: verify `neo4j+s://` and the exact `NEO4J_DATABASE` value from Aura.
- Approved tasks fail after planning: the CLI Agent is probably not running on `127.0.0.1:8001`.
- Adapter not found or CLI not found: install the selected assistant CLI and ensure it is on `PATH`.
- Empty retrieval results: run `scripts/ingest_demo.py` again and confirm Qdrant is reachable.

## License

Released under the [MIT License](LICENSE).
