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

## Local Agent Execution Depends On Installed Assistant CLI

**Status:** Open  
**Date:** 2026-03-22

### Current state

The new green-brand demo was verified end to end through ingestion, retrieval, risk classification, and approval routing.

The red-theme request works as intended because it stops before execution and is escalated for human approval.

The safe prompt path can still fail at the local execution stage if the selected coding assistant CLI is not installed correctly or the local CLI Agent cannot execute it.

### Practical impact

- The guardrail story is fully demoable without local execution because the violating prompt pauses before dispatch
- The full safe-execution path still depends on the local machine having a working assistant CLI such as `codex`, `claude`, or `cursor`
- If the assistant CLI is missing or misconfigured, retrieval and approval may still succeed while execution returns `failed`

### Workaround

- For the main live demo, use the red-theme prompt to show retrieval plus approval gating
- For full execution demos, verify the assistant CLI locally before presenting:
  - `codex --help`
  - `claude --help`
  - `cursor --help`
