# Known Issues

## Neo4j Aura — DatabaseNotFound on user queries

**Status:** Open
**Date:** 2026-03-22
**Severity:** Blocking for Neo4j-dependent features (graph retrieval)

### Symptom

The Neo4j Aura instance connects successfully via `bolt+s://` and system queries like `SHOW DATABASES` work. However, any user query (e.g., `RETURN 1 AS n`) fails with:

```
neo4j.exceptions.ClientError: {code: Neo.ClientError.Database.DatabaseNotFound}
{message: Database 5de5a02f not found}
```

### What works

- DNS resolution to `5de5a02f.databases.neo4j.io` resolves to `35.189.250.174`
- TCP connectivity on port 7687 (HTTPS returns 200)
- `bolt+s://` connection and authentication succeed
- `SHOW DATABASES` returns the home database `5de5a02f` with `currentStatus: online`
- `driver.verify_connectivity()` passes

### What fails

- Any query routed to the home database (`RETURN 1`, `CREATE`, `MATCH`, etc.)
- Both `session.run()` and `driver.execute_query()` fail the same way
- Specifying `database_='neo4j'` also fails (database not found)
- The `neo4j+s://` protocol fails entirely (routing table error)

### Root cause (suspected)

The Aura instance reports the database as `online` but the actual database is not yet provisioned or accessible. This may be:

1. An Aura free-tier provisioning delay after instance creation/resume
2. A known issue with the Neo4j Python driver 5.28.x and newer Aura instances
3. An Aura-side inconsistency where the routing table and database state are out of sync

### Workarounds to try

1. Wait and retry — the database may become available after full provisioning
2. Pause and resume the instance from the Neo4j Aura Console
3. Delete and recreate the Aura instance
4. Try an older version of the Neo4j Python driver (e.g., 5.25.x)

### Impact

- `scripts/setup_neo4j.py` cannot create constraints/indexes
- `scripts/seed_data.py` skips Neo4j seeding
- Graph retrieval (`find_related_issues`, `find_file_dependencies`, `find_constraints_for_repo`) will fail at runtime
- All other services (Supabase, Qdrant, Gemini) are unaffected

### Code notes

- All Neo4j code uses `bolt+s://` (auto-converted from `neo4j+s://`)
- `NEO4J_DATABASE` env var must be unset — the driver auto-reads it and it causes routing failures
- Once the database is accessible, run `uv run python scripts/setup_neo4j.py` to create the schema
