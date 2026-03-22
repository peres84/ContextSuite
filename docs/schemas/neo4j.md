# Neo4j Graph Schema

## Connection Notes

- Use `bolt+s://` protocol (not `neo4j+s://`) for Aura connections
- Unset `NEO4J_DATABASE` env var — the driver auto-reads it but Aura routing doesn't support it
- Queries use the home database automatically

## Node Labels

### Repository
| Property | Type | Description |
|---|---|---|
| id | string | Unique identifier (matches Supabase UUID) |
| name | string | Repository name (e.g., `acme/payments`) |
| url | string | Repository URL |

### Issue
| Property | Type | Description |
|---|---|---|
| id | string | Unique identifier |
| title | string | Issue title |
| status | string | Status: `open`, `closed`, `resolved` |
| severity | string | Severity: `low`, `medium`, `high`, `critical` |

### File
| Property | Type | Description |
|---|---|---|
| id | string | Unique identifier |
| path | string | File path relative to repo root |
| language | string | Programming language |

### Entity
| Property | Type | Description |
|---|---|---|
| id | string | Unique identifier |
| name | string | Entity name (function, class, module) |
| kind | string | Entity kind: `function`, `class`, `module`, `variable` |

### Task
| Property | Type | Description |
|---|---|---|
| id | string | Unique identifier |
| run_id | string | ContextSuite run ID (matches Supabase) |
| prompt | string | The prompt that triggered this task |

### Constraint
| Property | Type | Description |
|---|---|---|
| id | string | Unique identifier |
| description | string | What the constraint requires |
| source | string | Where the constraint was defined |

## Relationships

| Relationship | From | To | Description |
|---|---|---|---|
| HAS_FILE | Repository | File | Repository contains file |
| HAS_ISSUE | Repository | Issue | Repository has issue |
| DEFINES | File | Entity | File defines entity |
| IMPORTS | File | File | File imports another file |
| CALLS | Entity | Entity | Entity calls another entity |
| AFFECTS | Issue | File | Issue affects file |
| RELATED_TO | Issue | Issue | Issues are related |
| TARGETS | Task | Repository | Task targets repository |
| TOUCHES | Task | File | Task modifies file |
| RESOLVES | Task | Issue | Task resolves issue |
| APPLIES_TO | Constraint | Repository/File | Constraint applies to target |

## Constraints (Uniqueness)

- `repo_id` — Repository.id is unique
- `issue_id` — Issue.id is unique
- `file_id` — File.id is unique
- `entity_id` — Entity.id is unique
- `task_id` — Task.id is unique
- `constraint_id` — Constraint.id is unique

## Indexes

- `file_path` — File.path
- `issue_status` — Issue.status
- `task_run_id` — Task.run_id
- `entity_name` — Entity.name

## Recovery

To recreate the schema:

```bash
uv run python scripts/setup_neo4j.py
```
