# Green Guard Demo Runbook

This guide explains how to run the new demo website and verify the main ContextSuite behavior:

- the website's primary brand color must stay green
- a request to change the main theme to red should be flagged before execution

This is the simplest reproducible demo in the repo for showing retrieved constraints changing the workflow outcome.

## What This Demo Proves

The `demo/` project is a small React landing page with a hard rule:

- the primary brand color must remain green

The demo memory includes:

- a brand constraint document
- a prior incident where a red redesign was rejected
- theme-system notes that point to the CSS variables used by the site

When you ask ContextSuite to change the main styling from green to red, the Context Agent should:

1. retrieve the green-brand rule
2. classify the request as high risk
3. require human approval before any execution happens

## Files Used By This Demo

- [README.md](/d:/Proyectos/hackathons/2026/heilbronn-hackathon/demo/README.md)
- [App.jsx](/d:/Proyectos/hackathons/2026/heilbronn-hackathon/demo/src/App.jsx)
- [styles.css](/d:/Proyectos/hackathons/2026/heilbronn-hackathon/demo/src/styles.css)
- [brand-color.md](/d:/Proyectos/hackathons/2026/heilbronn-hackathon/demo/docs/constraints/brand-color.md)
- [INC-2026-0001-red-theme-regression.md](/d:/Proyectos/hackathons/2026/heilbronn-hackathon/demo/docs/incidents/INC-2026-0001-red-theme-regression.md)
- [theme-system.md](/d:/Proyectos/hackathons/2026/heilbronn-hackathon/demo/docs/notes/theme-system.md)
- [ingest_brand_demo.py](/d:/Proyectos/hackathons/2026/heilbronn-hackathon/scripts/ingest_brand_demo.py)

## Prerequisites

You need:

- `.env` configured
- Supabase, Qdrant, Neo4j, and Gemini credentials working
- Python dependencies installed with `uv`
- optionally, a coding assistant CLI like `codex` if you want to test the safe execution path too

Install and verify:

```powershell
uv sync --all-packages
uv run pytest packages/context-agent/tests/test_workflow.py -q
uv run python scripts/test_all.py
```

## Fastest Demo Path

Use this path if you only want to prove the guardrail.

Important note:

- You do not need the CLI Agent for the red-theme prompt, because the run should stop at human approval before dispatch.

### 1. Ingest the demo memory

```powershell
uv run python scripts/ingest_brand_demo.py
```

Expected result:

- it clears old demo chunks if they already exist
- it ingests 3 demo documents
- test retrieval returns 3 results

### 2. Start the Context Agent

```powershell
uv run context-agent
```

Optional health check:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health
```

### 3. Initialize the demo workspace

```powershell
uv run contextsuite -p ./demo init -r "demo/green-brand-site" -a codex
uv run contextsuite -p ./demo status
```

### 4. Run the red-theme prompt

```powershell
uv run contextsuite -p ./demo chat "Refresh the landing page styling and change the primary color from green to red across the hero, buttons, badges, and highlights."
```

Expected behavior:

- retrieved context mentions the green-brand rule
- `risk.level` becomes `high`
- `approval.status` becomes `escalated`
- the run waits for human approval
- no execution happens unless you approve it

If you just want to prove the guardrail, reject the request and stop there.

## Full Demo Path

Use this path if you also want to show a normal safe request.

### 1. Start the React app

In a separate terminal:

```powershell
cd demo
npm install
npm run dev
```

This should start the demo site on:

- `http://127.0.0.1:4173`

### 2. Start both agents

Terminal 1:

```powershell
uv run context-agent
```

Terminal 2:

```powershell
uv run cli-agent
```

### 3. Run a safe prompt

```powershell
uv run contextsuite -p ./demo chat "Improve the layout spacing, make the testimonials section clearer, and keep the primary green theme."
```

Expected workflow behavior:

- retrieval should return the theme notes, green constraint, and past incident
- risk should remain `low` or `medium`
- approval should be automatic
- execution should proceed only if your selected assistant CLI is installed and working

Important note:

- The safe path is now verified on a clean runtime path.
- If it still fails locally, the most common cause is a stale CLI-agent listener already holding port `8001`.

### 4. Run the blocked-by-constraint prompt

```powershell
uv run contextsuite -p ./demo chat "Refresh the landing page styling and change the primary color from green to red across the hero, buttons, badges, and highlights."
```

This is the main story for the live demo.

## Direct API Demo

If you want predictable JSON output for a presentation, use the API directly.

### Legacy HTTP request

```powershell
$body = @'
{
  "prompt": "Refresh the landing page styling and change the primary color from green to red across the hero, buttons, badges, and highlights.",
  "repository": "demo/green-brand-site",
  "assistant": "codex"
}
'@

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/tasks/send" `
  -ContentType "application/json" `
  -Body $body | ConvertTo-Json -Depth 8
```

Expected fields:

- `status: "pending_human_approval"`
- `risk.level: "high"`
- `risk.reason` mentions the retrieved brand-color conflict
- `approval.status: "escalated"`
- `task_id: null`

### A2A JSON-RPC request

```powershell
$body = @'
{
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
          "text": "Refresh the landing page styling and change the primary color from green to red across the hero, buttons, badges, and highlights."
        },
        {
          "kind": "data",
          "data": {
            "repository": "demo/green-brand-site",
            "assistant": "codex"
          }
        }
      ]
    }
  }
}
'@

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/a2a/contextsuite-context-agent" `
  -ContentType "application/json" `
  -Body $body | ConvertTo-Json -Depth 12
```

Expected fields:

- `result.status.state: "input-required"`
- returned task is tied to the Context Agent run
- the status payload reflects that approval is required before execution

## What Was Verified

The following paths were verified during development:

- `uv run python scripts/ingest_brand_demo.py`
- retrieval for `demo/green-brand-site`
- live red-theme request through `POST /tasks/send`

Verified red-theme result:

- risk is `high`
- reason is `violates retrieved constraint: primary brand color must remain green; requested red`
- approval is `escalated`

## Troubleshooting

### Ingestion fails in Qdrant

The current scripts now create the needed `repository_id` payload index automatically, so rerun:

```powershell
uv run python scripts/ingest_brand_demo.py
```

### Retrieval shows duplicate results

The demo ingest script now clears old demo chunks before re-ingesting. If needed, just rerun the same ingest command.

### Safe prompt fails during execution

That is usually a local runtime issue, not a retrieval issue. Check:

- `uv run cli-agent` is running
- port `8001` is not already occupied by an older CLI-agent process
- your selected assistant CLI is installed
- the assistant command is available on `PATH`

If you suspect `8001` is stale, run both agents on a clean port:

Terminal 1:

```powershell
$env:CLI_AGENT_PORT='8012'
uv run cli-agent
```

Terminal 2:

```powershell
$env:CLI_AGENT_PORT='8012'
uv run context-agent
```

Then rerun the same `contextsuite` command.

### Red prompt is approved but still appears to ignore the new fix

This usually means your shell started a new CLI Agent, but it could not bind to `8001` because an older listener was already running there.

Symptoms:

- `uv run cli-agent` exits quickly
- `http://127.0.0.1:8001/health` still responds
- the workflow still behaves like the older broken process

Workaround:

- free the old listener, or
- use the clean-port flow above with `CLI_AGENT_PORT='8012'`

### The React site does not start

Run from `demo/`:

```powershell
npm install
npm run dev
```

## Best Live Presentation Order

For the clearest demo:

1. show the website in `demo/`
2. show the constraint doc that says green must stay green
3. run `uv run python scripts/ingest_brand_demo.py`
4. send the red-theme prompt
5. show that ContextSuite retrieves the constraint and escalates before execution
6. explain that this is the product: the agent can propose, but the context and policy layer decides whether it is safe to proceed
