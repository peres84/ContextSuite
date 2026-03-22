# Context Agent Workflow

The Context Agent uses a LangGraph `StateGraph` to process prompts through a fixed pipeline. Each node reads from and writes to a shared `AgentState` dictionary. The graph is defined in `packages/context-agent/contextsuite_agent/workflow/graph.py`.

## Pipeline

```
intake → retrieve → plan → classify → approve →┬→ package → END
                                                └→ END (rejected)
```

If the task is approved, it flows to `package`. If rejected (high risk or policy violation), the graph ends immediately after `approve`.

Implementation note: the current graph also runs a synchronous `dispatch` step after `package`, which sends the task to the CLI Agent and waits for the result before returning the final API response.

## State

Defined in `workflow/state.py` as `AgentState(TypedDict)`:

| Field | Set by | Description |
|---|---|---|
| `prompt` | caller | The developer's prompt text |
| `repository` | caller | Repository name (e.g. `acme/payments`) |
| `assistant` | caller | Target coding assistant (`codex`, `claude`, `cursor`) |
| `run_id` | intake | UUID for this run (created in Supabase) |
| `trace_id` | intake | UUID for tracing across services |
| `repository_id` | intake | Supabase UUID for the repository (resolved from name) |
| `context_summary` | retrieve | Formatted text of retrieved context |
| `plan` | plan | Generated task plan (markdown) |
| `risk` | classify | `RiskAssessment` with level, signals, reason |
| `approval` | approve | `ApprovalDecision` with approved/rejected, reviewer, reason |
| `task_id` | package | UUID for the A2A task to dispatch |
| `payload` | package | `TaskPayload` object ready for A2A delivery |
| `dispatch_status` | package, dispatch | `ready`, `completed`, `failed`, `cli_agent_unreachable`, or `skipped_not_approved` |
| `dispatch_result` | dispatch | Raw result returned by the CLI Agent |

## Nodes

All nodes are in `workflow/nodes/`. Each is a plain function `(AgentState) -> AgentState`.

### 1. intake (`nodes/intake.py`)

- Looks up the repository by name in Supabase
- Creates a new `runs` record (status: `pending`)
- Persists the prompt in the `prompts` table
- Updates run status to `retrieving`
- Outputs: `run_id`, `trace_id`, `repository_id`

### 2. retrieve (`nodes/retrieve.py`)

- Calls `retrieve_context(prompt, repository_id=...)` which:
  - Embeds the prompt via Gemini Embedding 2 (3072-dim vector)
  - Searches Qdrant for the 8 most similar documents (cosine similarity)
  - Optionally queries Neo4j for related issues and constraints (best-effort, skipped if Neo4j is down)
  - Ranks and merges results
- Saves a `context_snapshots` record in Supabase (summary + source metadata)
- Updates run status to `planning`
- Outputs: `context_summary`

### 3. plan (`nodes/plan.py`)

- Sends the prompt + retrieved context to Gemini 2.5 Flash
- System prompt instructs Gemini to produce: summary, steps, affected files, risks/constraints
- Temperature: 0.3 (focused, low creativity)
- Saves the plan in the `plans` table
- Updates run status to `reviewing`
- Outputs: `plan`

### 4. classify (`nodes/classify.py`)

- Scans the prompt and plan text against regex patterns
- **High-risk patterns** (weight 0.8): `delete`, `drop`, `remove all`, `force push`, `production`, `migration`, `secret`, `auth*`, `payment`, `billing`
- **Medium-risk patterns** (weight 0.4): `refactor`, `update dependencies`, `api`, `schema`, `config`
- Level is determined by highest signal weight and signal count
- Outputs: `risk` (RiskAssessment with level, signals list, reason)

### 5. approve (`nodes/approve.py`)

- **Policy check**: blocklist of dangerous patterns (`drop database`, `rm -rf /`, `delete all users`, `disable authentication`). If matched, immediately rejected.
- **Low risk**: auto-approved (reviewer: `auto`)
- **Medium risk**: auto-approved in MVP mode (reviewer: `auto-mvp`). In production, would require human review.
- **High risk**: rejected (reviewer: `auto`). Would require human approval in production.
- Persists the decision in the `approvals` table
- Updates run status to `approved` or `rejected`
- Outputs: `approval`

### 6. package (`nodes/package.py`)

- Only runs if approved
- Builds a `TaskPayload` (A2A contract) containing: run_id, trace_id, prompt, plan, context_summary, risk_level, assistant, repository
- Generates a `task_id` for the A2A dispatch
- Updates run status to `dispatched`
- Outputs: `task_id`, `payload`, `dispatch_status`

### 7. dispatch (`nodes/dispatch.py`)

- Sends the packaged task to the CLI Agent over HTTP
- Waits for the CLI Agent result
- Persists the outcome in Supabase
- Updates the run status to `completed` or `failed`
- Outputs: `dispatch_status`, `dispatch_result`

## HTTP API

The workflow is exposed via `POST /tasks/send` on the Context Agent server (`server.py`).

### Request

```json
{
  "prompt": "Fix the webhook handler to validate optional email fields",
  "repository": "acme/payments",
  "assistant": "codex"
}
```

### Response

```json
{
  "run_id": "47274bac-...",
  "trace_id": "90aea668-...",
  "status": "completed",
  "plan": "This task involves modifying a webhook handler...",
  "context_summary": "1. [vector] Bug: Payment webhook handler crashes...",
  "risk": {
    "level": "low",
    "reason": "no risk signals detected",
    "signals": []
  },
  "approval": {
    "approved": true,
    "reason": "Auto-approved: low risk task",
    "reviewer": "auto"
  },
  "task_id": "5e447cd0..."
}
```

For rejected tasks, `status` is `"skipped_not_approved"`, `task_id` is `null`, and `approval.approved` is `false`.

## Supabase tables touched

Each run creates or updates records in these tables (in order):

1. `repositories` — looked up by name (read-only)
2. `runs` — created, then status updated at each step
3. `prompts` — one record per run
4. `context_snapshots` — one record with summary and source metadata
5. `plans` — one record with the generated plan text
6. `approvals` — one record with the decision, risk level, reviewer, and violations

## External services called

| Service | Node | Purpose |
|---|---|---|
| Supabase | intake, retrieve, plan, approve, package | Persistence (runs, prompts, snapshots, plans, approvals) |
| Gemini Embedding 2 | retrieve | Embed the prompt into a 3072-dim vector |
| Qdrant Cloud | retrieve | Semantic similarity search |
| Neo4j Aura | retrieve | Graph queries for related issues/constraints (optional, best-effort) |
| Gemini 2.5 Flash | plan | Generate the task plan from prompt + context |
| CLI Agent | dispatch | Execute the approved task with the selected assistant CLI |
