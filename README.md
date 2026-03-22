# ContextSuite

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

## Workflow

![ContextSuite workflow](docs/workflow.png)

## Why It Exists

AI coding tools are fast, but they often lose important project context over time. Teams repeat bugs, miss constraints, and forget why past decisions were made. ContextSuite keeps that memory available at the moment a change is requested.

## MVP Goal

Build a demo where a user sends a prompt to ContextSuite, ContextSuite reviews the task, then forwards an approved job over A2A to a Local Agent Client that runs Codex, Claude Code, or Cursor CLI and returns the result.

## How The MVP Works

1. User sends a prompt to the Context Agent.
2. Context Agent retrieves relevant history, constraints, and prior issues.
3. Context Agent prepares or reviews an implementation plan.
4. Low-risk tasks are auto-approved; riskier ones can require human approval.
5. The approved task is sent over A2A to the ContextSuite Local Agent Client.
6. The Local Agent Client runs the selected coding assistant CLI.
7. Results, approvals, and important issue-related outcomes are stored for future runs.

## Architecture Snapshot

- Orchestration: LangGraph
- Agent-to-agent communication: A2A
- Local execution bridge: ContextSuite Local Agent Client
- Coding assistants for MVP: Codex CLI, Claude Code CLI, Cursor CLI
- Model and embeddings: Gemini + Gemini Embedding 2 multimodal
- Relational system of record: Supabase
- Vector retrieval: Qdrant Cloud
- Relationship graph: Neo4j Aura

## A2A And MCP

ContextSuite is A2A-first.

A2A is the protocol between the Context Agent and the Local Agent Client. MCP is optional and internal to the Context Agent when extra tools are needed. It is not the main transport for coding-agent execution.

## Project Structure

```
packages/
  shared/              Shared A2A contracts, agent cards, and types (Pydantic)
  context-agent/       Context Agent — LangGraph workflow, retrieval, persistence
  cli-agent/           CLI Agent — local client that runs coding assistant CLIs
docs/
  architecture.md      Full folder layout and package descriptions
  plan.md              MVP execution checklist
```

See [`docs/architecture.md`](docs/architecture.md) for the complete folder tree.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)

## Local Setup

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

## Available Commands

| Command | Description |
|---|---|
| `uv run context-agent` | Start the Context Agent server |
| `uv run cli-agent` | Start the CLI Agent server |
| `uv run ruff check packages/` | Lint all packages |
| `uv run ruff format packages/` | Format all packages |
| `uv run pytest` | Run tests |

## Near-Term Outcome

Prove a simple end-to-end flow:

- one prompt in
- one reviewed plan
- one approved A2A task
- one coding assistant execution
- one stored memory trail

## License

Released under the [MIT License](LICENSE).
