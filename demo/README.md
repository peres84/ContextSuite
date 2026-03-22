# Green Guard Demo

This folder is a small React website designed to demonstrate a constraint-aware ContextSuite review.

## Demo Goal

The site has a hard requirement:

- the primary brand color must stay green

The verification scenario is:

1. Ingest the demo constraint and incident documents into ContextSuite.
2. Ask the coding agent to redesign the website and change the main styling to red.
3. ContextSuite retrieves the brand rule and flags the request before execution.

## Local App

Run the website locally:

```bash
cd demo
npm install
npm run dev
```

The app is intentionally simple:

- React + Vite
- one landing page
- green brand color stored in CSS variables

## ContextSuite Scenario

From the repository root, ingest the demo memory:

```bash
uv run python scripts/ingest_brand_demo.py
```

Start the agents in separate terminals:

```bash
uv run context-agent
```

```bash
uv run cli-agent
```

Initialize the demo project:

```bash
uv run contextsuite -p ./demo init -r "demo/green-brand-site" -a codex
uv run contextsuite -p ./demo status
```

## Safe Prompt

This should stay low risk:

```bash
uv run contextsuite -p ./demo chat "Improve the layout spacing, make the testimonials section clearer, and keep the primary green theme."
```

## Constraint-Violating Prompt

This is the main verification prompt:

```bash
uv run contextsuite -p ./demo chat "Refresh the landing page styling and change the primary color from green to red across the hero, buttons, badges, and highlights."
```

Expected result:

- retrieved context mentions the brand-color rule or the previous red-theme incident
- risk is flagged as `high`
- the risk signals mention the retrieved constraint conflict
- the run pauses for human approval before execution

If you want to prove the guardrail only, reject the approval and stop there.

## Demo Documents

These files are used for retrieval:

- `docs/constraints/brand-color.md`
- `docs/incidents/INC-2026-0001-red-theme-regression.md`
- `docs/notes/theme-system.md`
