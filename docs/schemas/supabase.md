# Supabase Schema

## Enums

```sql
create type risk_level as enum ('low', 'medium', 'high');

create type run_status as enum (
  'pending', 'retrieving', 'planning', 'reviewing',
  'approved', 'rejected', 'dispatched',
  'working', 'completed', 'failed', 'cancelled'
);

create type approval_decision as enum ('approved', 'rejected', 'escalated');
```

## Tables

### repositories

| Column | Type | Nullable | Default |
|---|---|---|---|
| id | uuid | no | gen_random_uuid() |
| name | text | no | |
| url | text | yes | |
| description | text | yes | |
| created_at | timestamptz | no | now() |
| updated_at | timestamptz | no | now() |

### runs

| Column | Type | Nullable | Default |
|---|---|---|---|
| id | uuid | no | gen_random_uuid() |
| trace_id | uuid | no | gen_random_uuid() |
| repository_id | uuid (FK → repositories) | yes | |
| status | run_status | no | 'pending' |
| risk | risk_level | no | 'low' |
| assistant | text | no | 'codex' |
| created_at | timestamptz | no | now() |
| updated_at | timestamptz | no | now() |

### prompts

| Column | Type | Nullable | Default |
|---|---|---|---|
| id | uuid | no | gen_random_uuid() |
| run_id | uuid (FK → runs) | no | |
| content | text | no | |
| repository_id | uuid (FK → repositories) | yes | |
| assistant | text | no | 'codex' |
| created_at | timestamptz | no | now() |

### plans

| Column | Type | Nullable | Default |
|---|---|---|---|
| id | uuid | no | gen_random_uuid() |
| run_id | uuid (FK → runs) | no | |
| content | text | no | |
| version | int | no | 1 |
| created_at | timestamptz | no | now() |

### context_snapshots

| Column | Type | Nullable | Default |
|---|---|---|---|
| id | uuid | no | gen_random_uuid() |
| run_id | uuid (FK → runs) | no | |
| summary | text | yes | |
| sources | jsonb | no | '[]' |
| created_at | timestamptz | no | now() |

### approvals

| Column | Type | Nullable | Default |
|---|---|---|---|
| id | uuid | no | gen_random_uuid() |
| run_id | uuid (FK → runs) | no | |
| decision | approval_decision | no | |
| risk | risk_level | no | 'low' |
| reason | text | yes | |
| reviewer | text | no | 'auto' |
| policy_violations | jsonb | no | '[]' |
| created_at | timestamptz | no | now() |

### outcomes

| Column | Type | Nullable | Default |
|---|---|---|---|
| id | uuid | no | gen_random_uuid() |
| run_id | uuid (FK → runs) | no | |
| task_id | text | yes | |
| status | text | no | |
| summary | text | yes | |
| output | text | yes | |
| artifacts | jsonb | no | '[]' |
| duration_seconds | float | yes | |
| error_code | text | yes | |
| error_message | text | yes | |
| created_at | timestamptz | no | now() |

### documents

| Column | Type | Nullable | Default |
|---|---|---|---|
| id | uuid | no | gen_random_uuid() |
| repository_id | uuid (FK → repositories) | yes | |
| source_type | text | no | |
| source_path | text | yes | |
| title | text | yes | |
| content | text | no | |
| chunk_index | int | no | 0 |
| chunk_total | int | no | 1 |
| vector_id | text | yes | |
| metadata | jsonb | no | '{}' |
| created_at | timestamptz | no | now() |
| updated_at | timestamptz | no | now() |

## Indexes

- `idx_runs_repository` on runs(repository_id)
- `idx_runs_status` on runs(status)
- `idx_runs_created` on runs(created_at DESC)
- `idx_prompts_run` on prompts(run_id)
- `idx_plans_run` on plans(run_id)
- `idx_approvals_run` on approvals(run_id)
- `idx_outcomes_run` on outcomes(run_id)
- `idx_context_snapshots_run` on context_snapshots(run_id)
- `idx_documents_repository` on documents(repository_id)
- `idx_documents_source_type` on documents(source_type)
- `idx_documents_vector_id` on documents(vector_id)

## Triggers

- `trg_runs_updated` — auto-updates `updated_at` on runs
- `trg_repositories_updated` — auto-updates `updated_at` on repositories
- `trg_documents_updated` — auto-updates `updated_at` on documents

## Recovery

To recreate from scratch, run the migration in `scripts/` or apply via Supabase MCP:

```bash
# The migration is applied via mcp__supabase__apply_migration
# See the create_core_tables migration
```
