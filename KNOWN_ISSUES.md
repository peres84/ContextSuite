# Known Issues

## A2A Protocol Compatibility

**Status:** Partially Resolved
**Date:** 2026-03-22

### Current state

The project now exposes real A2A-compatible discovery and JSON-RPC endpoints on both servers.

### Implemented

- Agent card discovery at `/.well-known/agent-card.json`
- A2A assistant endpoints at `/a2a/{assistant_id}`
- JSON-RPC `message/send` on the Context Agent and CLI Agent
- JSON-RPC `tasks/get` on the Context Agent and CLI Agent
- Context Agent -> CLI Agent dispatch now prefers the real A2A wire protocol
- Legacy endpoints remain available for backward compatibility:
  - Context Agent: `/tasks/send`, `/tasks/{run_id}/approval`
  - CLI Agent: `/tasks/receive`

### Remaining gaps

- `message/stream` is not implemented yet
- Push notifications are not implemented
- Non-blocking/background task execution is not implemented yet
- `stateTransitionHistory` is not implemented
- Context Agent `tasks/get` is backed by persisted run data, but CLI Agent `tasks/get` is process-local in-memory state only

### Practical impact

- The project is now interoperable with A2A clients for synchronous `message/send` flows and task polling
- The implementation should be described as real A2A JSON-RPC support with partial protocol coverage, not full end-to-end A2A feature coverage

## Neo4j Aura - Resolved

**Status:** Resolved  
**Date:** 2026-03-22

### Root cause

The Neo4j Aura free-tier database is named after the instance ID (for example `5de5a02f`), not `neo4j`. The previous code converted `neo4j+s://` to `bolt+s://` and did not specify the database, causing `DatabaseNotFound` errors.

### Fix

- Use `neo4j+s://` protocol with routing
- Do not convert to `bolt+s://`
- Pass `database=NEO4J_DATABASE` explicitly when opening sessions
- Set `NEO4J_DATABASE` in `.env` to the Aura instance ID

### Current state

- Schema created: 6 uniqueness constraints, 4 indexes
- Demo data seeded: 22 nodes and 35 relationships
- Graph retrieval functions verified working

## Local Agent Execution Depends On Installed Assistant CLI And Clean Agent Ports

**Status:** Partially Resolved
**Date:** 2026-03-22

### Current state

The green-brand demo is now verified end to end on a clean runtime path.

The remaining operational risk is no longer the adapter code itself. The main failure mode is starting a new agent while an older listener is still bound to the same port.

### Implemented fix

- CLI-agent subprocess execution was moved to a Windows-safe worker-thread subprocess path
- The Codex adapter now uses the current `codex exec` command shape
- Packaged `context-agent` and `cli-agent` entrypoints now default to `reload = false`

### Remaining caveat

- If port `8001` is already occupied by an older CLI-agent process, `uv run cli-agent` can fail to bind and your requests will still hit the stale process
- In that situation, the demo can still look broken even though the new code is correct
- The selected coding assistant CLI must still be installed and callable from `PATH`

### Practical impact

- The guardrail story remains fully demoable because the violating prompt escalates before execution
- The full approval-resume execution path works when the agent ports are clean and the assistant CLI is available
- If an old process still owns `8001`, the default local demo commands can hit stale behavior and appear to ignore recent fixes

### Workaround

- Kill any older CLI-agent listener before starting a new one, or run both agents on a clean alternate port
- For alternate-port runs, set `CLI_AGENT_PORT` for both services before starting them
- Verify the assistant CLI locally before presenting:
  - `codex --help`
  - `claude --help`
  - `cursor --help`
- If port `8001` is suspicious, use:
  - Terminal 1: `$env:CLI_AGENT_PORT='8012'; uv run cli-agent`
  - Terminal 2: `$env:CLI_AGENT_PORT='8012'; uv run context-agent`
