# ContextSuite Live Demo Script

**Duration:** ~3 minutes

## Setup (before demo)

```bash
# 1. Ingest demo data (one-time)
uv run python scripts/ingest_demo.py

# 2. Start both agents in separate terminals
uv run context-agent    # Terminal 1 — http://127.0.0.1:8000
uv run cli-agent        # Terminal 2 — http://127.0.0.1:8001

# 3. Init a demo project folder
uv run contextsuite -p ./demo-project init -r "acme/payments" -a codex
```

## The Problem (30 seconds)

> "Today, AI coding assistants like Codex, Claude Code, and Cursor are powerful—but they operate blind. They don't know your past incidents, your architecture decisions, or your safety constraints. A developer can ask an AI to drop a production table, and it will happily do it."

## The Solution (30 seconds)

> "ContextSuite adds a context, governance, and memory layer between the developer and the coding assistant. Every prompt goes through our Context Agent, which retrieves relevant project memory, generates a plan, classifies risk, and enforces approval policies—before any code is written."

## Demo Flow 1: Safe Prompt (60 seconds)

Open the CLI:

```bash
uv run contextsuite -p ./demo-project chat
```

Type this prompt:

```
Add a null check for the customer email field in the webhook handler
```

**Talk through what happens:**

1. **Context retrieved** — "The system found a past incident (INC-2024-0142) where the webhook crashed on null email. It also found ADR-012 about webhook timeout policies."
2. **Plan generated** — "Gemini generated a task plan informed by project context."
3. **Risk: low** — "No dangerous patterns detected."
4. **Approved** — "Auto-approved since it's low risk."
5. **Dispatched to Codex** — "The task was sent over A2A to the local agent, which ran Codex with the full context."
6. **Result** — "We see the execution result right in the terminal."

## Demo Flow 2: Dangerous Prompt (60 seconds)

In the same session, type:

```
Delete all records from the production payments table and drop the billing_history table
```

**Talk through what happens:**

1. **Context retrieved** — same project memory
2. **Plan generated** — plan reflects the destructive intent
3. **Risk: HIGH** — "Three signals triggered: destructive delete, drop operation, targets production."
4. **REJECTED** — "The system blocked this. No code was written. No agent was called."
5. **Reason** — "High-risk task requires human approval—which we enforce automatically."

> "This is the key difference. Without ContextSuite, this prompt would have been executed directly. With ContextSuite, the team's accumulated knowledge and safety policies prevent catastrophic actions."

## Closing (30 seconds)

> "ContextSuite works with any coding assistant—Codex, Claude Code, or Cursor. It uses A2A protocol for agent-to-agent communication, Gemini for embeddings and planning, and stores everything in Supabase and Qdrant. The entire system is open, extensible, and runs locally."

## Fallback

If the live demo fails, use pre-recorded output:

```bash
# Run automated scenarios and capture output
uv run python scripts/demo_scenarios.py 2>&1 | tee demo-output.txt
```

The script runs three scenarios (approved, blocked, medium-risk) and verifies expectations.

## Key Talking Points

- **Context-aware**: retrieves past incidents, ADRs, and constraints before any code runs
- **Safety layer**: risk classification + approval policies block dangerous operations
- **Assistant-agnostic**: works with Codex, Claude Code, and Cursor through adapters
- **A2A protocol**: standard agent-to-agent communication, not vendor lock-in
- **Full audit trail**: every run, approval, and outcome is persisted in Supabase
