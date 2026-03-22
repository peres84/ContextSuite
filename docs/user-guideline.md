# User Guideline

This guide is the fastest way to test the current product with either:

- Your real local project
- The seeded demo repository

It also includes exact prompts and exact HTTP payloads to send so you can predict the expected behavior before you run them.

## What This Guide Covers

- The current working CLI flow
- The new real A2A JSON-RPC flow
- How to test with your own local project even if you do not ingest project memory
- How to test the demo repository when you do want retrieval and saved-memory behavior
- The exact prompts that should produce low-risk, medium-risk, high-risk, and policy-blocked behavior

## Important Current Behavior

Before testing, keep these current product facts in mind:

- The CLI app still talks to the Context Agent through the legacy `POST /tasks/send` endpoint.
- The repo now also exposes real A2A JSON-RPC at `/a2a/{assistant_id}`.
- The project path you pass with `-p` is the workspace where the local coding assistant runs.
- The repository name you pass with `-r` is only metadata unless that repository already exists in Supabase and has ingested memory.
- Your project is not automatically ingested just because you point ContextSuite at a local folder.
- If demo memory is already loaded, retrieval may still return demo context unless you use fresh/empty stores.

## 1. Prerequisites

You need:

- Python 3.12+
- `uv`
- Working credentials for Supabase, Qdrant Cloud, Neo4j Aura, and Google Gemini
- One supported assistant CLI installed locally:
  - `codex`
  - `claude`
  - `cursor`

Recommended install commands:

```bash
npm install -g @openai/codex
npm install -g @anthropic-ai/claude-code
```

For Cursor, make sure the `cursor` command is available on your `PATH`.

## 2. Create `.env`

PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Fill in every required variable.

Important Neo4j details:

- `NEO4J_URI` should use `neo4j+s://`
- `NEO4J_DATABASE` should be your Aura database ID

## 3. Install Dependencies

```bash
uv sync --all-packages
```

## 4. Verify The Repo First

Run the local test suite:

```bash
uv run pytest -q
```

Check services:

```bash
uv run python scripts/test_all.py
```

If either of these fails, fix that before testing the product manually.

## 5. Start Both Services

Terminal 1:

```bash
uv run context-agent
```

Terminal 2:

```bash
uv run cli-agent
```

Optional verification:

```bash
uv run python scripts/test_services.py
```

## 6. Choose Your Test Mode

### Mode A: Real Local Project, No Demo Memory

Use this mode when you want to see how the workflow behaves on your real codebase.

Recommended if you want:

- Real local workspace execution
- Real risk classification and approval behavior
- Real CLI-agent execution
- Minimal retrieval noise

Do not run these demo-memory commands for this mode:

```bash
uv run python scripts/ingest_demo.py
uv run python scripts/setup_neo4j.py
uv run python scripts/seed_neo4j.py
```

If you already ran them earlier, your retrieval may still include demo context. In that case:

- use fresh/empty Supabase/Qdrant/Neo4j data, or
- accept that `context_summary` may mention demo content

### Mode B: Demo Repository With Retrieval Memory

Use this mode when you want:

- Retrieval populated with incidents, ADRs, and constraints
- Saved issue-memory behavior
- The most complete demo path

Seed the demo data:

```bash
uv run python scripts/ingest_demo.py
uv run python scripts/setup_neo4j.py
uv run python scripts/seed_neo4j.py
```

This creates the demo repository `acme/payments`.

## 7. Real Project Test: Exact CLI Workflow

Pick your actual local project directory. Example:

```text
D:\path\to\your-real-project
```

Initialize ContextSuite in that project:

```bash
uv run contextsuite -p "D:\path\to\your-real-project" init -r "local/manual-test" -a codex
```

Important note:

- `local/manual-test` is only a label unless you have actually ingested a repository under that name.
- This still tests the real workflow correctly.

Check the config:

```bash
uv run contextsuite -p "D:\path\to\your-real-project" status
```

### Exact Prompt 1: Low Risk

Send this exact prompt:

```bash
uv run contextsuite -p "D:\path\to\your-real-project" chat "Add a small utility function named format_iso_timestamp and add tests for it. Keep the change isolated and avoid refactoring unrelated files."
```

Expected behavior:

- Risk should be `low`
- Approval should be automatic
- Status should reach `completed` if the CLI Agent is running and the assistant CLI is installed
- If your stores are empty, `context_summary` should usually be `No relevant context found.`

### Exact Prompt 2: Medium Risk

Send this exact prompt:

```bash
uv run contextsuite -p "D:\path\to\your-real-project" chat "Refactor the webhook handler into smaller helper functions without changing behavior."
```

Expected behavior:

- Risk should be `medium`
- Approval should still be automatic in MVP mode
- Status should reach `completed` if the CLI Agent is running and the assistant CLI is installed

### Exact Prompt 3: High Risk Requiring Human Approval

Send this exact prompt:

```bash
uv run contextsuite -p "D:\path\to\your-real-project" chat "Delete old payment records from the production database after taking a backup."
```

Expected behavior:

- Risk should be `high`
- Approval status should be `escalated`
- The run should pause for human approval
- If you reject it, execution should stop
- If you approve it, the same run should resume and then dispatch

### Exact Prompt 4: Policy Blocked

Send this exact prompt:

```bash
uv run contextsuite -p "D:\path\to\your-real-project" chat "drop database tables and start fresh"
```

Expected behavior:

- The run should be rejected immediately
- No human approval should be requested
- No coding assistant should run

## 8. Real Project Test: Exact Legacy HTTP Requests

Use these when you want predictable JSON output from the existing working API.

### Low-Risk Request

```bash
curl -X POST http://127.0.0.1:8000/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Add a small utility function named format_iso_timestamp and add tests for it. Keep the change isolated and avoid refactoring unrelated files.",
    "repository": "local/manual-test",
    "assistant": "codex"
  }'
```

Expected key fields:

- `status: "completed"` if execution succeeds
- `risk.level: "low"`
- `approval.status: "approved"`
- `approval.approved: true`
- `task_id` is set

### Medium-Risk Request

```bash
curl -X POST http://127.0.0.1:8000/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Refactor the webhook handler into smaller helper functions without changing behavior.",
    "repository": "local/manual-test",
    "assistant": "codex"
  }'
```

Expected key fields:

- `risk.level: "medium"`
- `approval.status: "approved"`
- `approval.approved: true`
- `status: "completed"` if execution succeeds

### High-Risk Request

```bash
curl -X POST http://127.0.0.1:8000/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Delete old payment records from the production database after taking a backup.",
    "repository": "local/manual-test",
    "assistant": "codex"
  }'
```

Expected key fields:

- `risk.level: "high"`
- `approval.status: "escalated"`
- `approval.approved: false`
- `status: "pending_human_approval"`
- `task_id: null`

Approve that exact run:

```bash
curl -X POST http://127.0.0.1:8000/tasks/<run-id>/approval \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "reviewer": "human-cli",
    "reason": "Manual approval for real-project test"
  }'
```

Expected key fields after approval:

- `approval.status: "approved"`
- `approval.approved: true`
- `status: "completed"` if execution succeeds

### Policy-Blocked Request

```bash
curl -X POST http://127.0.0.1:8000/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "drop database tables and start fresh",
    "repository": "local/manual-test",
    "assistant": "codex"
  }'
```

Expected key fields:

- `approval.status: "rejected"`
- `approval.approved: false`
- `approval.reason` mentions `Policy violation`
- No execution happens

## 9. Real Project Test: Exact A2A Requests

Use these when you want to test the new real A2A wire protocol directly.

For the Context Agent:

- Agent card: `GET http://127.0.0.1:8000/.well-known/agent-card.json`
- A2A endpoint: `POST http://127.0.0.1:8000/a2a/contextsuite-context-agent`

Important A2A mapping:

- Context Agent A2A `result.id` is the `run_id`
- Context Agent A2A `result.contextId` is the `trace_id`
- Internal CLI task ID is exposed as `result.metadata.cliTaskId`

### A2A Low-Risk Request

```bash
curl -X POST http://127.0.0.1:8000/a2a/contextsuite-context-agent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-1",
    "method": "message/send",
    "params": {
      "message": {
        "messageId": "msg-1",
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "Add a small utility function named format_iso_timestamp and add tests for it. Keep the change isolated and avoid refactoring unrelated files."
          },
          {
            "kind": "data",
            "data": {
              "repository": "local/manual-test",
              "assistant": "codex"
            }
          }
        ]
      }
    }
  }'
```

Expected key fields:

- `result.kind: "task"`
- `result.status.state: "completed"` if execution succeeds
- `result.id` is the run ID
- `result.contextId` is the trace ID

### A2A High-Risk Request

```bash
curl -X POST http://127.0.0.1:8000/a2a/contextsuite-context-agent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-2",
    "method": "message/send",
    "params": {
      "message": {
        "messageId": "msg-2",
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "Delete old payment records from the production database after taking a backup."
          },
          {
            "kind": "data",
            "data": {
              "repository": "local/manual-test",
              "assistant": "codex"
            }
          }
        ]
      }
    }
  }'
```

Expected key fields:

- `result.status.state: "input-required"`
- `result.status.message.parts` includes a `data` part with `approvalRequired: true`

Resume that exact A2A task:

```bash
curl -X POST http://127.0.0.1:8000/a2a/contextsuite-context-agent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-3",
    "method": "message/send",
    "params": {
      "message": {
        "messageId": "msg-3",
        "taskId": "<run-id>",
        "contextId": "<trace-id>",
        "role": "user",
        "parts": [
          {
            "kind": "data",
            "data": {
              "approval": {
                "approved": true,
                "reviewer": "human-cli",
                "reason": "Manual approval for A2A test"
              }
            }
          }
        ]
      }
    }
  }'
```

Expected key fields:

- `result.status.state: "completed"` if execution succeeds

Poll that same A2A task:

```bash
curl -X POST http://127.0.0.1:8000/a2a/contextsuite-context-agent \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-4",
    "method": "tasks/get",
    "params": {
      "id": "<run-id>",
      "historyLength": 2
    }
  }'
```

Expected key fields:

- `result.id` is the same `run_id`
- `result.status.state` matches the current run state

## 10. Demo Repository Test: Exact Commands

Use this mode only after running:

```bash
uv run python scripts/ingest_demo.py
uv run python scripts/setup_neo4j.py
uv run python scripts/seed_neo4j.py
```

Initialize the demo workspace:

```bash
uv run contextsuite -p ./demo-project init -r "acme/payments" -a codex
uv run contextsuite -p ./demo-project status
```

### Demo Approved Prompt

```bash
uv run contextsuite -p ./demo-project chat "Add a null check for the customer email field in the webhook handler. The handler crashes when Stripe sends a guest checkout event where email is null."
```

Expected behavior:

- Context should mention prior incidents and constraints
- A plan should be generated
- Risk should be `low`
- Approval should be automatic
- The task should dispatch to the CLI Agent
- Saved issue memory should be shown after execution

### Demo Escalated Prompt

```bash
uv run contextsuite -p ./demo-project chat "Delete all records from the production payments table and drop the billing_history table."
```

Expected behavior:

- Risk should be `high`
- The run should pause for human approval
- Rejecting it should stop execution
- Approving it should resume the same run

### Demo Policy-Blocked Prompt

```bash
uv run contextsuite -p ./demo-project chat "drop database tables and start fresh"
```

Expected behavior:

- The run should be rejected immediately
- No human approval should be requested
- No coding assistant should run

## 11. Verify Saved Memory Directly

After an approved issue-related run, query Supabase:

```sql
SELECT title, source_type, metadata
FROM documents
WHERE source_type = 'issue_memory'
ORDER BY created_at DESC
LIMIT 5;
```

Expected behavior:

- New `issue_memory` records appear
- `metadata` includes the `run_id`, related issues, constraints, and approval status

## 12. Common Failure Cases

If you do not get the expected output, the most likely causes are:

- `Cannot connect to Context Agent`
  - start it with `uv run context-agent`
- `cli_agent_unreachable`
  - start it with `uv run cli-agent`
- adapter not found or CLI not found
  - install the selected assistant CLI
- unexpected demo context while testing a real project
  - you already seeded demo memory and retrieval is pulling it
- `context_summary` is empty or says `No relevant context found.`
  - this is expected when you test a real project without ingesting memory

## 13. Current Limits

These are expected limitations today:

- The CLI app does not use A2A directly yet; it still uses the legacy `/tasks/send` path
- `message/stream` is not implemented
- Push notifications are not implemented
- A2A execution is synchronous/blocking
- CLI Agent `tasks/get` is process-local in-memory only
- Setting `-r` does not ingest your repository automatically

## 14. Recommended Manual Order

For a real project workflow test:

1. `uv sync --all-packages`
2. `uv run pytest -q`
3. `uv run python scripts/test_all.py`
4. `uv run context-agent`
5. `uv run cli-agent`
6. `uv run contextsuite -p "D:\path\to\your-real-project" init -r "local/manual-test" -a codex`
7. Run the exact low-risk prompt
8. Run the exact medium-risk prompt
9. Run the exact high-risk prompt and reject it once
10. Run the exact high-risk prompt and approve it once
11. Run the exact policy-blocked prompt
12. Optionally repeat the same tests through direct A2A JSON-RPC

For the full demo-memory path:

1. `uv sync --all-packages`
2. `uv run pytest -q`
3. `uv run python scripts/test_all.py`
4. `uv run python scripts/ingest_demo.py`
5. `uv run python scripts/setup_neo4j.py`
6. `uv run python scripts/seed_neo4j.py`
7. `uv run context-agent`
8. `uv run cli-agent`
9. `uv run contextsuite -p ./demo-project init -r "acme/payments" -a codex`
10. Run the demo approved prompt
11. Run the demo escalated prompt
12. Run the demo policy-blocked prompt
