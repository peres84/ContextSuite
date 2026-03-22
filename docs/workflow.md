# Context Agent Workflow

The Context Agent uses a LangGraph `StateGraph` to process prompts through a fixed pipeline. Each node reads from and writes to a shared `AgentState` dictionary. The graph is defined in `packages/context-agent/contextsuite_agent/workflow/graph.py`.

## Pipeline

```text
intake -> retrieve -> plan -> classify -> approve -> package -> dispatch -> save_memory -> END
                                              |
                                              +-> END (rejected or escalated)
```

Low-risk and MVP medium-risk tasks continue automatically. Policy-violating tasks are rejected immediately. High-risk tasks are escalated for human approval and pause before packaging. When a human approves, the server rebuilds the persisted run state, dispatches the task, and saves issue-related memory.

## State

Defined in `workflow/state.py` as `AgentState(TypedDict)`:

| Field | Set by | Description |
|---|---|---|
| `prompt` | caller | The developer's prompt text |
| `repository` | caller | Repository name (for example `acme/payments`) |
| `assistant` | caller | Target coding assistant (`codex`, `claude`, `cursor`) |
| `run_id` | intake | UUID for this run |
| `trace_id` | intake | UUID for cross-service tracing |
| `repository_id` | intake | Supabase UUID for the repository |
| `context_summary` | retrieve | Formatted retrieved context |
| `context_sources` | retrieve | Structured retrieved sources used for later memory saving |
| `plan` | plan | Generated task plan |
| `risk` | classify | `RiskAssessment` with level, signals, and reason |
| `approval` | approve | `ApprovalDecision` with `approved`, `rejected`, or `escalated` status |
| `task_id` | package | UUID for the A2A task |
| `payload` | package | `TaskPayload` ready for A2A delivery |
| `dispatch_status` | package, dispatch | `ready`, `completed`, `failed`, `cli_agent_unreachable`, `pending_human_approval`, or `skipped_not_approved` |
| `dispatch_result` | dispatch | Raw result returned by the CLI Agent |
| `saved_memory` | save_memory | Summary of durable issue memory saved after execution |

## Nodes

### 1. `intake`

- Looks up the repository by name in Supabase.
- Creates the `runs` row and persists the prompt.
- Moves the run to `retrieving`.

### 2. `retrieve`

- Embeds the prompt via Gemini Embedding 2.
- Searches Qdrant for similar docs.
- Optionally queries Neo4j for related issues and constraints.
- Saves a `context_snapshots` record with summary and structured sources.
- Moves the run to `planning`.

### 3. `plan`

- Sends the prompt and retrieved context to Gemini 2.5 Flash.
- Stores the generated plan in `plans`.
- Moves the run to `reviewing`.

### 4. `classify`

- Scans prompt and plan text for high- and medium-risk patterns.
- Produces a `RiskAssessment`.
- Persists the current run risk level.

### 5. `approve`

- Blocks explicit policy violations immediately.
- Auto-approves low risk.
- Auto-approves medium risk in MVP mode.
- Escalates high risk for human approval and records an `escalated` approval entry.

### 6. `package`

- Runs only when approved.
- Builds the `TaskPayload`.
- Assigns a `task_id`.
- Moves the run to `dispatched`.

### 7. `dispatch`

- Sends the packaged task to the CLI Agent over HTTP.
- Waits synchronously for the result.
- Persists the outcome in `outcomes`.
- Moves the run to `completed` or `failed`.

### 8. `save_memory`

- Runs after dispatch.
- Extracts the actual issue and constraint references from retrieved context.
- Saves durable `issue_memory` documents for issue-related runs.
- Falls back to plain Supabase document storage if vector-backed ingestion fails.

## HTTP API

### `POST /tasks/send`

Request:

```json
{
  "prompt": "Fix the webhook handler to validate optional email fields",
  "repository": "acme/payments",
  "assistant": "codex"
}
```

Example completed response:

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
    "status": "approved",
    "reason": "Auto-approved: low risk task",
    "reviewer": "auto"
  },
  "task_id": "5e447cd0...",
  "saved_memory": {
    "saved": true,
    "title": "Issue memory for run 47274bac",
    "reason": "Saved issue-related memory for future retrieval"
  }
}
```

For high-risk tasks, `status` is `pending_human_approval`, `task_id` is `null`, and `approval.status` is `escalated`.

### `POST /tasks/{run_id}/approval`

Use this endpoint to resolve an escalated run:

```json
{
  "approved": true,
  "reviewer": "human-cli",
  "reason": "Reviewed and approved by operator"
}
```

If approved, the server resumes packaging, dispatch, and memory saving. If rejected, the run is marked rejected and does not dispatch.

## Supabase Tables Touched

1. `repositories`
2. `runs`
3. `prompts`
4. `context_snapshots`
5. `plans`
6. `approvals`
7. `outcomes`
8. `documents` for durable `issue_memory`

## External Services Called

| Service | Node | Purpose |
|---|---|---|
| Supabase | intake, retrieve, plan, approve, package, dispatch, save_memory | Persistence for runs, prompts, plans, approvals, outcomes, and issue memory |
| Gemini Embedding 2 | retrieve, save_memory | Prompt embeddings and durable issue-memory embeddings |
| Qdrant Cloud | retrieve, save_memory | Semantic search and vector-backed issue memory |
| Neo4j Aura | retrieve | Related issues and constraints |
| Gemini 2.5 Flash | plan | Task planning |
| CLI Agent | dispatch | Execute the approved task |
