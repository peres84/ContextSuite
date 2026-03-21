# ContextSuite Extended Plan

## 1. Project Summary
ContextSuite is a specialized context and governance suite for coding assistants. Its goal is to prevent regression of previously approved logic by preserving historical issue context, solution rationale, trust signals, and policy constraints.

Core principle: complete a working Context Agent workflow demo first. Multi-tenant provider onboarding is optional and must be implemented only if time remains.

## 2. Product Identity
- Product name: ContextSuite
- Protocol name: A2C (Agent-to-Context)
- Positioning: AI governance and memory layer for coding assistants

## 3. Objectives
- Prevent repeated logic regressions in long coding sessions.
- Persist why a fix was implemented and what must not be changed.
- Provide plan-time guardrails before code execution.
- Support human approval for medium/high risk modifications.
- Build a complete context-assistant-focused suite with search, research, docs, skills, and MCP-accessible tooling.

## 4. Scope and Priority
## In scope (mandatory)
- End-to-end Context Agent workflow demo.
- Storage integration with PostgreSQL, Qdrant, and Neo4j.
- Policy checks and trust scoring.
- Retrieval, negotiation, approval, and indexing lifecycle.
- Tooling interfaces for search, research, docs, skills, and MCP endpoints.

## Out of scope until demo is accepted
- Public landing page for self-service company onboarding.
- Multi-tenant billing and subscription workflows.
- Enterprise admin panel and advanced provisioning.
- VS Code extension UI integration (optional after core MCP command workflow is stable).

## 5. Stack Decisions
- Orchestration: LangGraph (LangChain ecosystem)
- Inter-agent communication: A2C protocol boundary
- Model and embeddings: Gemini (reasoning + Gemini Embedding 2 multimodal)
- Vector retrieval: Qdrant
- System of record and audit: PostgreSQL
- Relationship reasoning: Neo4j

## 6. High-Level Architecture
- Context Agent API (MVP default)
  - Receives A2C requests directly from user/coder agents for hackathon speed.
  - Keeps routing simple: direct input to Context Agent first, then plan/review loop.
- Optional production control plane/gateway
  - Add later for multi-tenant auth, rate limits, advanced policy enforcement, and billing/control functions.
- Workflow Engine (LangGraph)
  - Executes deterministic stages: retrieve, review, negotiate, approve, authorize, index.
- Memory and Policy Stores
  - PostgreSQL: transactional state, approvals, audit, trust history.
  - Qdrant: semantic search over issues/fixes/changelogs/constraints summaries.
  - Neo4j: dependency and contradiction graph for impact analysis.
- Tool Integration Layer
  - Search, research, docs/skills lookup, MCP tool adapters.
- Observability
  - Traces, decisions, latency, and retrieval confidence.

## 7. Canonical Data Responsibilities
- PostgreSQL
  - Issues, fixes, validations, approvals, constraints metadata.
  - Commit evidence for issue-related flows:
    - repo, branch, commit_sha, parent_sha, pr_number, merge_commit_sha.
    - author, committer, committed_at, commit_message, files_changed_count.
    - linked issue_id, fix_id, approval_decision_id for traceability.
  - Diff summaries (not full patches by default): changed symbols, key value/constant changes, risk tags, affected modules.
  - Full patch storage only for high-risk/compliance-required issue flows.
  - Preference storage (source of truth):
    - user_preferences (developer-level defaults such as risk tolerance, notification channels, preferred assistant behavior).
    - team_preferences (approval policy overrides, protected modules, coding standards, escalation rules).
    - project_preferences (repo-specific constraints, release windows, branch/merge policies).
  - Approval attribution fields are mandatory for every non-auto approval:
    - approved_by_user_id, approved_by_name, approver_role, approval_source.
    - approved_at, approval_reason, approval_conditions, decision_version.
  - Auto-approval attribution fields are mandatory for low-risk decisions:
    - decision_mode=auto, policy_id, policy_version, evaluated_signals, confidence_score.
  - Trust score snapshots and lifecycle states.
  - Immutable audit entries for every decision and transition.
- Qdrant
  - Embeddings for issue text, prompts, root-cause summaries, fix summaries, changelog summaries, constraints narratives.
  - Optional embeddings for preference narratives and team policy summaries to improve retrieval context for planning.
  - Metadata payload filters: state, risk, tags, project/module.
- Neo4j
  - Graph entities and relationships: BLOCKS, CONTRADICTS, SUPERSEDES, DEPENDS_ON, REQUIRES_APPROVAL.
  - Preference and ownership relationships:
    - USER_PREFERS_POLICY, TEAM_OWNS_MODULE, TEAM_REQUIRES_APPROVAL_FROM_ROLE, PROJECT_INHERITS_TEAM_POLICY.
  - Impact-chain expansion during plan review.

## 8. A2C Core Workflow
0. Input Routing Policy (default-first gate)
- Default rule: for any existing project, all user prompts must go to Context Agent first.
- Context Agent performs pre-checks before any coding assistant execution:
  - task classification (new feature, bugfix, refactor, research)
  - context retrieval (prior issues, constraints, approved rationale)
  - risk and approval routing decision
- Bypass rule: only for truly new project bootstrapping (no prior repo/context), user can start directly with coding assistant.
- After project initialization, routing switches back to Context Agent first for all subsequent prompts.

1. Context Agent Intake (first entry point)
- Input request arrives from user to Context Agent.
- Context Agent classifies task type and risk, then prepares a context brief.

2. Context Retrieval and Briefing
- Qdrant semantic recall for similar issues and fixes.
- PostgreSQL symbolic filters (state, severity, trust thresholds, constraints).
- Neo4j expansion for dependency and contradiction paths.
- Context Agent sends a pre-execution brief to coder agent, including recommended approach and must-not-break constraints.

3. Coder Agent Plan Submission
- Coder agent creates an implementation plan and sends it back to Context Agent for review.

4. Context Agent Review and Decision
- Context Agent checks the plan against must-not-break constraints, known issue history, and risk policy.
- Context Agent performs git-aware checks (read-only): compare approved plan scope versus proposed/actual diff scope.
- Drift checks include: extra files changed, sensitive symbols touched, risky constant/config value changes.
- If compliant: mark as approvable.
- If not compliant: return violation details and request plan refinement.

5. Approval Routing (auto or delegated)
- Low-risk: controlled auto-approval.
- Medium/high-risk: delegate to human approval.
- Approval record must always include who/what approved:
  - Human: approver identity, role, timestamp, rationale, and any conditions.
  - Auto: policy version, evaluated signals, confidence, and generated decision trace.
- Context Agent issues execution token only after approval.

6. Execute or Refine Loop
- If approved: coder agent executes using the execution token.
- If not approved: coder agent refines plan and resubmits to Context Agent.
- Repeat until approved or explicitly rejected.

7. Post-Execution Indexing
- Indexing is issue-driven only: persist/index data only when the task is tied to a detected issue, regression, violation, or explicit problem case.
- If no issue/problem is detected, skip indexing to avoid memory noise and reduce false historical signals.
- For issue-related tasks, persist outcome, rationale, and evidence in PostgreSQL.
- For issue-related tasks, persist commit evidence and diff summary linked to issue/fix/approval records.
- For issue-related tasks, update embeddings in Qdrant.
- For issue-related tasks, update graph relationships in Neo4j.
- Recompute trust scores and lifecycle transitions only for issue-related records.

## 9. Trust Scoring and Lifecycle
- Lifecycle states: proposed, applied, validated, superseded, contradicted.
- Trust updates on:
  - validation evidence (increase)
  - human approvals (increase)
  - contradictions/regressions (decrease)
  - time decay and stale evidence (decrease)
- Score is deterministic and auditable.

## 10. ContextSuite Tooling Suite
ContextSuite must expose a practical tool suite for coding assistants:
- Code and issue search.
- Git inspection tools (read-only by default): git diff/show/log/blame and changed-files analysis.
- Research and reference retrieval.
- Skills/documentation retrieval.
- MCP-accessible tools where available.
- Unified response schema including source references and confidence.

Primary integration mode:
- MCP command-based workflow is the default integration path for MVP.
- Context Agent and coder agent interactions must work fully through MCP commands first.
- For hackathon, keep transport simple: commands call Context Agent API directly (no extra gateway required).

Optional integration mode:
- VS Code extension can be added later as an optional UX layer on top of MCP commands.
- Extension scope is UI convenience only (prompt intake, approval buttons, status view), not core orchestration logic.

Git permission policy:
- Default for Context Agent: read-only git access.
- Optional controlled write actions: PR comments/status checks only.
- Forbidden for Context Agent by default: force-push, branch deletion, destructive history rewrites.

### MCP Command Contract (MVP)
- `a2c.submit_task`: submit user prompt/context to Context Agent and start routing.
- `a2c.get_context_brief`: retrieve issue/risk/constraint brief for coder planning.
- `a2c.submit_plan`: submit structured coder plan for review.
- `a2c.review_plan`: return decision (`approved`, `refine`, `blocked`) with reasons.
- `a2c.request_approval`: delegate approval for medium/high risk tasks.
- `a2c.issue_execution_token`: issue token when approval requirements are satisfied.
- `a2c.report_execution_result`: report execution outcome and trigger issue-only indexing.

## 11. Demo Acceptance Criteria (Mandatory)
A working demo is accepted only if all conditions pass:
- For existing projects, user prompts are routed to Context Agent first and logged with routing decision.
- A known recurring bug is detected using historical context before code execution.
- A plan that breaks prior approved logic is blocked or forced into negotiation.
- A safe revised plan is approved and executed.
- PostgreSQL, Qdrant, and Neo4j are all updated consistently after execution.
- Indexing is performed only for issue-related flows; non-issue successful tasks do not create historical issue-memory records.
- Trust score and lifecycle state changes are visible and explainable.
- Logs show clear evidence of prevented regression.

## 12. Implementation Phases
## Phase 1: Scope Lock and Contracts
- Freeze product/protocol naming.
- Freeze demo-first delivery strategy.
- Define A2C request/response contracts and error semantics.

## Phase 2: Workflow Runtime
- Implement LangGraph state machine for A2C flow.
- Add policy gates and fail-safe write blocking.

## Phase 3: Data Layer Integration
- Implement PostgreSQL schema and audit writes.
- Implement Qdrant indexing/retrieval.
- Implement Neo4j relationship updates and traversal queries.

## Phase 4: Retrieval and Policy Quality
- Tune hybrid retrieval.
- Add must-not-break extraction and violation checks.
- Validate trust score updates and transitions.

## Phase 5: Tooling Suite Integration
- Connect search, research, docs/skills, and MCP tools.
- Keep MCP command flow as the required execution path for demo.
- Normalize outputs and attach evidence.

## Phase 6: End-to-End Demo Hardening
- Run scripted scenarios.
- Add observability dashboards/log views.
- Validate latency and failure recovery.

## Phase 6.5 (Optional Production Architecture)
Only if time remains after demo acceptance criteria.
- Add gateway/control-plane layer for multi-tenant auth, quotas, and advanced routing.
- Add asynchronous queueing/retry patterns for higher reliability.
- Add enterprise-grade controls (tenant isolation hardening, policy version rollout, billing hooks).

## Phase 7 (Optional Last): Provider Onboarding Page
Only start if all mandatory demo criteria are done.
- Build simple onboarding page.
- Generate credentials and connection URL.
- Keep minimal scope: no full billing/control plane.
- Optional: lightweight VS Code extension UI that consumes existing MCP commands and Context Agent APIs.

## 13. Risks and Mitigations
- Cross-store inconsistency risk
  - Mitigation: idempotent writes, shared correlation IDs, retry-safe indexing jobs.
- False-positive guardrails
  - Mitigation: confidence thresholds, explainable violation reasons, human override path.
- Latency from multi-store retrieval
  - Mitigation: staged retrieval, caching, and timeout policies.
- Scope creep
  - Mitigation: strict rule that onboarding UI is optional final phase.

## 14. Deliverables
- A2C workflow implementation and protocol docs.
- Integrated PostgreSQL, Qdrant, Neo4j data pipelines.
- Trust scoring and lifecycle module.
- Tool suite adapters and normalized response schema.
- Demo script and evidence report showing regression prevention.
- Optional: onboarding page and credential flow.

## 15. Final Priority Rule
If schedule is constrained, prioritize:
1) Workflow correctness
2) Retrieval and indexing integrity across all stores
3) Policy and approval behavior
4) Demo evidence quality
5) Optional onboarding page
