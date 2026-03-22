# Known Issues

## Neo4j Aura — RESOLVED

**Status:** Resolved
**Date:** 2026-03-22

### Root cause

The Neo4j Aura free-tier database is named after the instance ID (e.g., `5de5a02f`), not `neo4j`. The previous code converted `neo4j+s://` to `bolt+s://` and didn't specify the database, causing `DatabaseNotFound` errors.

### Fix

- Use `neo4j+s://` protocol (with routing) — do NOT convert to `bolt+s://`
- Pass `database=NEO4J_DATABASE` explicitly when opening sessions
- Set `NEO4J_DATABASE=5de5a02f` in `.env` (the Aura instance ID)

### Current state

- Schema created: 6 uniqueness constraints, 4 indexes
- Demo data seeded: 22 nodes (1 repo, 9 files, 3 issues, 6 entities, 3 constraints), 35 relationships
- All graph retrieval functions verified working
