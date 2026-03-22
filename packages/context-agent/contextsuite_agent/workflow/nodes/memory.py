"""Issue-memory persistence node."""

from __future__ import annotations

import logging
import re

from contextsuite_agent.ingestion.pipeline import ingest_document
from contextsuite_agent.ingestion.sources import DocumentSource, SourceType
from contextsuite_agent.persistence import DocumentsRepo
from contextsuite_agent.workflow.state import AgentState

logger = logging.getLogger(__name__)

ISSUE_ID_RE = re.compile(r"(INC-\d{4}-\d+|ISSUE-\d+)", re.IGNORECASE)
CONSTRAINT_ID_RE = re.compile(r"(CON-\d+|ADR-\d+)", re.IGNORECASE)


def _match_reference(pattern: re.Pattern[str], *candidates: str) -> str | None:
    for candidate in candidates:
        match = pattern.search(candidate or "")
        if match:
            return match.group(1).upper()
    return None


def _dedupe_refs(refs: list[dict]) -> list[dict]:
    seen: set[tuple[str, str]] = set()
    deduped: list[dict] = []
    for ref in refs:
        key = (ref.get("id", ""), ref.get("title", ""))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(ref)
    return deduped


def extract_memory_references(context_sources: list[dict] | None) -> tuple[list[dict], list[dict]]:
    """Extract issue and constraint references from retrieved context sources."""
    issue_refs: list[dict] = []
    constraint_refs: list[dict] = []

    for source in context_sources or []:
        metadata = source.get("metadata") or {}
        content = source.get("content", "")
        source_name = source.get("source", "")
        source_type = (metadata.get("type") or "").lower()
        title = metadata.get("title") or ""
        path = metadata.get("file") or metadata.get("source") or ""

        issue_id = metadata.get("issue_id") or _match_reference(
            ISSUE_ID_RE,
            title,
            path,
            content,
        )
        if issue_id or source_type in {"incident", "issue"}:
            issue_refs.append({
                "id": issue_id or title or path or "issue-context",
                "title": title or content[:120],
                "source": source_name,
                "path": path or None,
                "status": metadata.get("status"),
            })

        constraint_id = metadata.get("constraint_id") or _match_reference(
            CONSTRAINT_ID_RE,
            title,
            path,
            content,
        )
        is_constraint_context = (
            constraint_id
            or source_type in {"constraint", "adr"}
            or content.lower().startswith("constraint:")
        )
        if is_constraint_context:
            constraint_refs.append({
                "id": constraint_id or title or path or "constraint-context",
                "title": title or content[:120],
                "source": source_name,
                "path": path or None,
            })

    return _dedupe_refs(issue_refs), _dedupe_refs(constraint_refs)


def should_persist_issue_memory(
    *,
    issue_refs: list[dict],
    constraint_refs: list[dict],
    outcome_state: str | None,
    policy_violations: list[str] | None,
) -> bool:
    return bool(
        issue_refs
        or constraint_refs
        or (policy_violations or [])
        or outcome_state == "failed"
    )


def build_issue_memory_content(
    state: AgentState,
    issue_refs: list[dict],
    constraint_refs: list[dict],
) -> str:
    """Build the durable memory content saved after an issue-related run."""
    run_id = state["run_id"]
    approval = state.get("approval")
    risk = state.get("risk")
    dispatch_result = state.get("dispatch_result") or {}

    lines = [
        f"# Issue Memory For Run {run_id}",
        "",
        f"Prompt: {state.get('prompt', '').strip()}",
        f"Outcome: {dispatch_result.get('state', state.get('dispatch_status', 'unknown'))}",
        (
            "Approval: "
            f"{getattr(approval, 'status', 'unknown')} by "
            f"{approval.reviewer if approval else 'unknown'}"
        ),
        f"Risk: {risk.level if risk else 'unknown'}",
    ]

    if approval and approval.reason:
        lines.append(f"Approval reason: {approval.reason}")

    summary = dispatch_result.get("summary")
    if summary:
        lines.extend(["", "Execution summary:", summary])

    if issue_refs:
        lines.extend(["", "Related issues:"])
        lines.extend(
            f"- {ref['id']}: {ref.get('title', '').strip()}" for ref in issue_refs
        )

    if constraint_refs:
        lines.extend(["", "Relevant constraints:"])
        lines.extend(
            f"- {ref['id']}: {ref.get('title', '').strip()}" for ref in constraint_refs
        )

    output = dispatch_result.get("output")
    if output:
        lines.extend(["", "Execution evidence:", output[:1500]])

    return "\n".join(lines).strip()


def save_memory(state: AgentState) -> AgentState:
    """Persist issue-related memory after dispatch when it adds future value."""
    run_id = state["run_id"]
    approval = state.get("approval")
    outcome_state = (
        (state.get("dispatch_result") or {}).get("state")
        or state.get("dispatch_status")
    )
    issue_refs, constraint_refs = extract_memory_references(state.get("context_sources"))
    policy_violations = approval.policy_violations if approval else []

    if not should_persist_issue_memory(
        issue_refs=issue_refs,
        constraint_refs=constraint_refs,
        outcome_state=outcome_state,
        policy_violations=policy_violations,
    ):
        return {
            **state,
            "saved_memory": {
                "saved": False,
                "reason": "No issue-related incidents, constraints, or failures were detected",
                "issue_refs": [],
                "constraint_refs": [],
            },
        }

    content = build_issue_memory_content(state, issue_refs, constraint_refs)
    title = f"Issue memory for run {run_id[:8]}"
    metadata = {
        "run_id": run_id,
        "task_id": state.get("task_id"),
        "approval_status": str(getattr(approval, "status", "unknown")),
        "risk_level": str(state["risk"].level) if state.get("risk") else "unknown",
        "issue_refs": issue_refs,
        "constraint_refs": constraint_refs,
        "outcome_state": outcome_state,
        "policy_violations": policy_violations,
    }
    source = DocumentSource(
        content=content,
        source_type=SourceType.ISSUE_MEMORY,
        title=title,
        source_path=f"runs/{run_id}/issue-memory.md",
        repository=state.get("repository"),
        repository_id=state.get("repository_id"),
        metadata=metadata,
    )

    stored_records: list[dict] = []
    vector_stored = False
    try:
        stored_records = ingest_document(source)
        vector_stored = bool(stored_records) and all(
            record.get("vector_id") for record in stored_records
        )
    except Exception:
        logger.exception("memory: vector-backed issue memory save failed for run=%s", run_id)
        stored_records = [
            DocumentsRepo.create_document(
                repository_id=state.get("repository_id"),
                source_type=SourceType.ISSUE_MEMORY.value,
                source_path=source.source_path,
                title=source.title,
                content=content,
                metadata=metadata,
            )
        ]

    return {
        **state,
        "saved_memory": {
            "saved": True,
            "title": title,
            "reason": "Saved issue-related memory for future retrieval",
            "document_ids": [record["id"] for record in stored_records],
            "vector_stored": vector_stored,
            "issue_refs": issue_refs,
            "constraint_refs": constraint_refs,
        },
    }
