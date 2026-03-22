# Demo Fallback Assets

Use this folder for demo-safe captured outputs when you want a backup to the live run.

## Generate a Fresh Fallback Transcript

With the Context Agent, CLI Agent, and demo data running:

```bash
uv run python scripts/demo_scenarios.py --json-out docs/fallback/demo-output.json
```

This produces a machine-readable transcript of:

- approved flow
- escalated then approved flow
- escalated then rejected flow
- policy-blocked flow
- medium-risk approved flow

## Suggested Usage

- Keep `demo-output.json` as a backup artifact before presenting.
- Pair it with terminal screenshots if you want a more judge-friendly fallback.
- Regenerate it after major workflow changes so it stays in sync with the product.
