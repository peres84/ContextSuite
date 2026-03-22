# Known Issues

## A2A Protocol Compatibility

**Status:** Open  
**Date:** 2026-03-22

### Issue

The project currently uses A2A-shaped contracts, task models, and agent cards, but it does not implement the real A2A wire protocol.

### Current behavior

- The Context Agent exposes custom endpoints such as `/tasks/send`
- The CLI Agent exposes a custom endpoint at `/tasks/receive`
- The handoff uses custom JSON over HTTP, not the standard A2A JSON-RPC methods
- The project does not yet expose the standard A2A endpoint shape such as `/a2a/{assistant_id}`
- The project does not yet implement standard A2A methods like `message/send`, `message/stream`, or `tasks/get`

### Impact

- The system is not currently interoperable with real A2A-compatible agents or platforms out of the box
- The current implementation should be described as A2A-inspired, not true A2A protocol compliance

### Planned fix

- Add real A2A-compatible endpoints and JSON-RPC request handling
- Keep the existing workflow and adapters, but move the transport layer to actual A2A protocol semantics

## Neo4j Aura - RESOLVED

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
