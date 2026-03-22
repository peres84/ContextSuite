# User Guideline

This guide is the fastest way to validate the current MVP yourself from a clean checkout.

## What You Will Verify

- The local test suite passes
- Cloud services are reachable
- Demo memory can be seeded
- The Context Agent and CLI Agent can run locally
- A low-risk prompt is approved and dispatched
- A dangerous prompt is blocked before execution

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

Copy the template:

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

- `NEO4J_URI` should use the `neo4j+s://` scheme
- `NEO4J_DATABASE` should be your Aura database ID
- Do not assume the database name is `neo4j`

## 3. Install dependencies

```bash
uv sync --all-packages
```

## 4. Run the local-only tests

This step does not require cloud access.

```bash
uv run pytest -q
```

If this fails, fix that before testing the full flow.

## 5. Check external services

Run all connectivity checks:

```bash
uv run python scripts/test_all.py
```

Or test services individually:

```bash
uv run python scripts/test_supabase.py
uv run python scripts/test_qdrant.py
uv run python scripts/test_neo4j.py
uv run python scripts/test_gemini.py
```

Expected result: each script should report a successful connection or a clear configuration error.

## 6. Seed the demo data

First ingest the textual demo context:

```bash
uv run python scripts/ingest_demo.py
```

Then set up and seed the Neo4j graph:

```bash
uv run python scripts/setup_neo4j.py
uv run python scripts/seed_neo4j.py
```

At the end you should have:

- Demo repository: `acme/payments`
- Supabase documents and run metadata
- Qdrant vectors for retrieval
- Neo4j nodes and relationships for issues, files, dependencies, and constraints

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

The health endpoints are:

- Context Agent: `http://127.0.0.1:8000/health`
- CLI Agent: `http://127.0.0.1:8001/health`

## 8. Initialize a demo workspace

```bash
uv run contextsuite -p ./demo-project init -r "acme/payments" -a codex
uv run contextsuite -p ./demo-project status
```

This creates `.contextsuite.json` in the target project directory.

## 9. Run an approved prompt

One-shot mode:

```bash
uv run contextsuite -p ./demo-project chat "Add a null check for the customer email field in the webhook handler. The handler crashes when Stripe sends a guest checkout event where email is null."
```

Expected behavior:

- Context is retrieved from prior incidents and constraints
- A plan is generated
- Risk is classified as `low`
- The task is approved
- The task is dispatched to the CLI Agent
- The selected assistant CLI runs in the local workspace

## 10. Run a blocked prompt

```bash
uv run contextsuite -p ./demo-project chat "Delete all records from the production payments table and drop the billing_history table."
```

Expected behavior:

- Risk is classified as `high`
- The task is rejected
- No coding assistant is executed

## 11. Use interactive mode

```bash
uv run contextsuite -p ./demo-project chat
```

Useful commands inside the session:

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

- File references are part of the request path today.
- Image attachment syntax exists in the CLI, but the current workflow is still text-first, so do not rely on image processing for the main demo.

## 12. Run the canned demo scenarios

With both services running:

```bash
uv run python scripts/demo_scenarios.py
```

Or run a single scenario:

```bash
uv run python scripts/demo_scenarios.py approved
uv run python scripts/demo_scenarios.py blocked
uv run python scripts/demo_scenarios.py medium
```

## 13. If you want to test the API directly

```bash
curl -X POST http://127.0.0.1:8000/tasks/send \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Add a null check for the customer email field in the webhook handler",
    "repository": "acme/payments",
    "assistant": "codex"
  }'
```

Approved requests require the CLI Agent to be running, because dispatch is synchronous in the current MVP.

## 14. Troubleshooting

### `Context Agent` is reachable but approved prompts fail

The CLI Agent is probably not running on `127.0.0.1:8001`.

### `Neo4j` fails with database errors

Check that `NEO4J_DATABASE` matches the Aura database ID exactly.

### `Supabase` or `Qdrant` connection is refused

Check the `.env` values first. The current test scripts will fail fast if the service URL or key is wrong.

### The assistant runs are rejected immediately

That is expected for high-risk or blocked prompts. Use the safe webhook null-check prompt first.

### The assistant CLI cannot be found

Install the selected assistant CLI and verify it is on your `PATH`.

## 15. Recommended manual test order

1. `uv run pytest -q`
2. `uv run python scripts/test_all.py`
3. `uv run python scripts/ingest_demo.py`
4. `uv run python scripts/setup_neo4j.py`
5. `uv run python scripts/seed_neo4j.py`
6. `uv run context-agent`
7. `uv run cli-agent`
8. `uv run contextsuite -p ./demo-project init -r "acme/payments" -a codex`
9. Run the approved prompt
10. Run the blocked prompt
