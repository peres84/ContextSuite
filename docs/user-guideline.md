# User Guideline

This guide is the fastest way to validate the current MVP from a clean checkout.

## What You Will Verify

- The local test suite passes
- Cloud services are reachable
- Demo memory can be seeded
- The Context Agent and CLI Agent can run locally
- A low-risk prompt is approved and dispatched
- A high-risk prompt pauses for human approval
- A policy-violating prompt is blocked immediately
- Issue-related memory is saved after completion

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

## 3. Install dependencies

```bash
uv sync --all-packages
```

## 4. Run local-only tests

```bash
uv run pytest -q
```

If this fails, fix that before testing the full flow.

## 5. Check external services

```bash
uv run python scripts/test_all.py
```

Or individually:

```bash
uv run python scripts/test_supabase.py
uv run python scripts/test_qdrant.py
uv run python scripts/test_neo4j.py
uv run python scripts/test_gemini.py
```

## 6. Seed the demo data

```bash
uv run python scripts/ingest_demo.py
uv run python scripts/setup_neo4j.py
uv run python scripts/seed_neo4j.py
```

At the end you should have:

- Demo repository: `acme/payments`
- Incidents, ADRs, and constraints in retrieval memory
- Neo4j issue and dependency graph data

## 7. Start both services

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

## 8. Initialize a demo workspace

```bash
uv run contextsuite -p ./demo-project init -r "acme/payments" -a codex
uv run contextsuite -p ./demo-project status
```

## 9. Run an approved prompt

```bash
uv run contextsuite -p ./demo-project chat "Add a null check for the customer email field in the webhook handler. The handler crashes when Stripe sends a guest checkout event where email is null."
```

Expected behavior:

- Context is retrieved from prior incidents and constraints
- A plan is generated
- Risk is `low`
- The task is auto-approved
- The task is dispatched to the CLI Agent
- The selected assistant CLI runs locally
- Saved issue memory is shown after execution

## 10. Run an escalated prompt

```bash
uv run contextsuite -p ./demo-project chat "Delete all records from the production payments table and drop the billing_history table."
```

Expected behavior:

- Risk is `high`
- The run pauses for human approval
- The CLI asks whether to approve the run
- Rejecting it stops execution
- Approving it resumes the same run and preserves the approval trail

## 11. Run a policy-blocked prompt

```bash
uv run contextsuite -p ./demo-project chat "drop database tables and start fresh"
```

Expected behavior:

- The run is rejected immediately by policy
- No human approval is requested
- No coding assistant is executed

## 12. Verify saved memory directly

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

## 13. Run the canned demo scenarios

With both services running:

```bash
uv run python scripts/demo_scenarios.py
```

Useful variants:

```bash
uv run python scripts/demo_scenarios.py approved
uv run python scripts/demo_scenarios.py escalated_approved
uv run python scripts/demo_scenarios.py escalated_rejected
uv run python scripts/demo_scenarios.py policy_blocked
uv run python scripts/demo_scenarios.py --json-out docs/fallback/demo-output.json
```

## 14. Use the API directly

Start a run:

```bash
curl -X POST http://127.0.0.1:8000/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Delete all records from the production payments table and drop the billing_history table.",
    "repository": "acme/payments",
    "assistant": "codex"
  }'
```

Resolve an escalated approval:

```bash
curl -X POST http://127.0.0.1:8000/tasks/<run-id>/approval \
  -H "Content-Type: application/json" \
  -d '{
    "approved": true,
    "reviewer": "human-cli",
    "reason": "Manual approval for demo"
  }'
```

## 15. Interactive mode tips

```bash
uv run contextsuite -p ./demo-project chat
```

Useful commands:

- `/help`
- `/status`
- `/context`
- `/assistant codex`
- `/assistant claude`
- `/assistant cursor`
- `/image path/to/image.png`
- `/quit`

Prompt features:

- `@path/to/file.py` attaches file content to the prompt
- `#image:path/to/image.png` attaches an image reference from the CLI

Current limitation:

- Image syntax exists in the CLI, but the workflow is still text-first, so do not rely on image processing for the main demo.

## 16. Recommended manual test order

1. `uv run pytest -q`
2. `uv run python scripts/test_all.py`
3. `uv run python scripts/ingest_demo.py`
4. `uv run python scripts/setup_neo4j.py`
5. `uv run python scripts/seed_neo4j.py`
6. `uv run context-agent`
7. `uv run cli-agent`
8. `uv run contextsuite -p ./demo-project init -r "acme/payments" -a codex`
9. Run the approved prompt
10. Run the escalated prompt and reject it once
11. Run the escalated prompt and approve it once
12. Run the policy-blocked prompt
13. Run `uv run python scripts/demo_scenarios.py`
