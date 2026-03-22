"""Ingest the green-brand demo context documents through the normal pipeline.

Usage: uv run python scripts/ingest_brand_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from contextsuite_agent.config import settings  # noqa: E402
from contextsuite_agent.ingestion import DocumentSource, SourceType, ingest_documents  # noqa: E402
from contextsuite_agent.persistence.client import get_supabase  # noqa: E402
from contextsuite_agent.retrieval import retrieve_context  # noqa: E402
from contextsuite_agent.retrieval.vector import get_qdrant  # noqa: E402

REPO_NAME = "demo/green-brand-site"
REPO_URL = "https://example.local/demo/green-brand-site"
REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_ROOT = REPO_ROOT / "demo"

DEMO_DOCS = [
    {
        "title": "Constraint: Primary brand color must stay green",
        "source_type": SourceType.CONSTRAINT,
        "source_path": "demo/docs/constraints/brand-color.md",
        "file_path": DEMO_ROOT / "docs" / "constraints" / "brand-color.md",
    },
    {
        "title": "INC-2026-0001: Temporary red redesign caused confusion",
        "source_type": SourceType.INCIDENT,
        "source_path": "demo/docs/incidents/INC-2026-0001-red-theme-regression.md",
        "file_path": DEMO_ROOT / "docs" / "incidents" / "INC-2026-0001-red-theme-regression.md",
    },
    {
        "title": "Theme system notes",
        "source_type": SourceType.CODE_SUMMARY,
        "source_path": "demo/docs/notes/theme-system.md",
        "file_path": DEMO_ROOT / "docs" / "notes" / "theme-system.md",
    },
]


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _clear_existing_demo_documents(repo_id: str) -> None:
    sb = get_supabase()
    existing = (
        sb.table("documents")
        .select("id, vector_id")
        .eq("repository_id", repo_id)
        .execute()
    )
    rows = existing.data or []
    if not rows:
        return

    vector_ids = [row["vector_id"] for row in rows if row.get("vector_id")]
    if vector_ids:
        get_qdrant().delete(settings.qdrant_collection, points_selector=vector_ids, wait=True)

    sb.table("documents").delete().eq("repository_id", repo_id).execute()
    print(f"Cleared {len(rows)} existing demo document chunks")


def main() -> None:
    sb = get_supabase()
    repos = sb.table("repositories").select("id").eq("name", REPO_NAME).execute()

    if repos.data:
        repo_id = repos.data[0]["id"]
        print(f"Using existing repository: {repo_id}")
    else:
        result = (
            sb.table("repositories")
            .insert({"name": REPO_NAME, "url": REPO_URL})
            .execute()
        )
        repo_id = result.data[0]["id"]
        print(f"Created repository: {repo_id}")

    _clear_existing_demo_documents(repo_id)

    sources = [
        DocumentSource(
            content=_load_text(doc["file_path"]),
            source_type=doc["source_type"],
            title=doc["title"],
            source_path=doc["source_path"],
            repository=REPO_NAME,
            repository_id=repo_id,
        )
        for doc in DEMO_DOCS
    ]

    print(f"Ingesting {len(sources)} demo documents...")
    records = ingest_documents(sources)
    print(f"Created {len(records)} document chunks in Supabase + Qdrant")

    results, summary = retrieve_context(
        "Refresh the landing page styling and change the primary color from green to red.",
        repository_id=repo_id,
    )
    print(f"\nTest retrieval: {len(results)} results")
    print(f"Top result score: {results[0].score:.2f}" if results else "No results")
    print(f"\n{summary}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
