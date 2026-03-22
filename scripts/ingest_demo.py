"""Ingest demo context documents through the pipeline.

Usage: uv run python scripts/ingest_demo.py

This replaces the manual seed_data.py with the proper ingestion pipeline,
which chunks documents, embeds them, stores vectors in Qdrant, and tracks
metadata in Supabase's documents table.
"""

from __future__ import annotations

import sys

from dotenv import load_dotenv

load_dotenv()

from contextsuite_agent.ingestion import DocumentSource, SourceType, ingest_documents  # noqa: E402
from contextsuite_agent.persistence.client import get_supabase  # noqa: E402

# ---------------------------------------------------------------------------
# Demo documents — realistic context for acme/payments repository
# ---------------------------------------------------------------------------

DEMO_DOCS: list[dict] = [
    {
        "title": "INC-2024-0142: Payment webhook crash on null email",
        "source_type": SourceType.INCIDENT,
        "source_path": "incidents/INC-2024-0142.md",
        "content": (
            "## Incident INC-2024-0142\n\n"
            "**Date:** 2024-11-15\n"
            "**Severity:** P1\n"
            "**Service:** payment-webhooks\n\n"
            "### Summary\n"
            "The payment webhook handler crashed when Stripe sent an event where "
            "the customer email field was null. The handler assumed email was always "
            "present and called `.lower()` on it, causing an AttributeError.\n\n"
            "### Root cause\n"
            "Guest checkout in Stripe does not require an email. The webhook handler "
            "at `src/webhooks/webhook_handler.py:handle_payment_success` did not "
            "validate optional fields before accessing them.\n\n"
            "### Resolution\n"
            "Added null-checks for all optional customer fields. Added a regression "
            "test for guest checkout webhooks.\n\n"
            "### Action items\n"
            "- All webhook handlers must validate optional fields before access\n"
            "- Add schema validation at the webhook entry point\n"
        ),
    },
    {
        "title": "ADR-007: Currency values stored in cents",
        "source_type": SourceType.ADR,
        "source_path": "docs/adr/ADR-007-currency-in-cents.md",
        "content": (
            "## ADR-007: Store currency values in cents (integer)\n\n"
            "**Status:** Accepted\n"
            "**Date:** 2024-08-20\n\n"
            "### Context\n"
            "Floating-point arithmetic causes rounding errors in financial "
            "calculations. Multiple bugs have resulted from storing prices as "
            "decimals.\n\n"
            "### Decision\n"
            "All monetary values are stored as integers representing cents. "
            "Display formatting converts cents to the locale-appropriate format "
            "at the presentation layer only.\n\n"
            "### Consequences\n"
            "- All database columns for money use `bigint`\n"
            "- API responses include both `amount_cents` (integer) and "
            "`amount_display` (formatted string)\n"
            "- Legacy data must be migrated from decimal to cents\n"
        ),
    },
    {
        "title": "Constraint: user-service API must not be called from webhooks",
        "source_type": SourceType.CONSTRAINT,
        "source_path": "docs/constraints/no-user-service-in-webhooks.md",
        "content": (
            "## Constraint: No user-service calls from webhook handlers\n\n"
            "**Source:** Architecture Review Board, 2024-09\n\n"
            "Webhook handlers must not make synchronous calls to the user-service. "
            "The user-service has a 99.5% SLA and webhook handlers must complete "
            "within 5 seconds. If user data is needed, it must be pre-fetched or "
            "read from a local cache.\n\n"
            "**Applies to:** All files under `src/webhooks/`\n"
            "**Enforcement:** Code review + CI lint rule (planned)\n"
        ),
    },
    {
        "title": "INC-2024-0098: Duplicate charge on retry storm",
        "source_type": SourceType.INCIDENT,
        "source_path": "incidents/INC-2024-0098.md",
        "content": (
            "## Incident INC-2024-0098\n\n"
            "**Date:** 2024-09-03\n"
            "**Severity:** P2\n"
            "**Service:** payment-processor\n\n"
            "### Summary\n"
            "A network blip caused the payment processor to retry a charge 4 times, "
            "resulting in duplicate charges to 23 customers.\n\n"
            "### Root cause\n"
            "The retry logic in `src/payments/charge.py` did not use idempotency "
            "keys. Stripe processed each retry as a new charge.\n\n"
            "### Resolution\n"
            "Added idempotency key generation using `run_id + payment_intent_id`. "
            "All Stripe API calls now include an idempotency key.\n\n"
            "### Action items\n"
            "- All external payment API calls must include idempotency keys\n"
            "- Add retry budget limits (max 3 retries with exponential backoff)\n"
        ),
    },
    {
        "title": "Code summary: retry logic in payment processor",
        "source_type": SourceType.CODE_SUMMARY,
        "source_path": "src/payments/charge.py",
        "content": (
            "## src/payments/charge.py\n\n"
            "The `charge_customer()` function handles payment processing through "
            "Stripe. Key behaviors:\n\n"
            "1. Generates an idempotency key from `run_id + payment_intent_id`\n"
            "2. Retries up to 3 times with exponential backoff (1s, 2s, 4s)\n"
            "3. Logs each attempt with trace_id for observability\n"
            "4. On final failure, raises `PaymentFailedError` with the Stripe "
            "error code\n"
            "5. All amounts are in cents (integer) per ADR-007\n\n"
            "**Dependencies:** stripe, payments.idempotency, payments.errors\n"
            "**Last incident:** INC-2024-0098 (duplicate charges)\n"
        ),
    },
    {
        "title": "ADR-012: Webhook handler timeout policy",
        "source_type": SourceType.ADR,
        "source_path": "docs/adr/ADR-012-webhook-timeout.md",
        "content": (
            "## ADR-012: Webhook handlers must complete within 5 seconds\n\n"
            "**Status:** Accepted\n"
            "**Date:** 2024-10-10\n\n"
            "### Context\n"
            "Stripe retries webhooks after 20 seconds. If our handler takes too "
            "long, we receive duplicate events. Past incidents (INC-2024-0098) "
            "showed that slow handlers combined with retries cause duplicate "
            "processing.\n\n"
            "### Decision\n"
            "All webhook handlers must complete within 5 seconds. Long-running "
            "work must be dispatched to a background queue. The webhook handler "
            "should only validate, enqueue, and return 200.\n\n"
            "### Consequences\n"
            "- Handlers must not call slow external services synchronously\n"
            "- Background workers process the actual business logic\n"
            "- Monitoring alerts if p99 handler latency exceeds 3 seconds\n"
        ),
    },
]


def main() -> None:
    """Run the demo ingestion."""
    # Look up or create the demo repository
    sb = get_supabase()
    repos = sb.table("repositories").select("id").eq("name", "acme/payments").execute()

    if repos.data:
        repo_id = repos.data[0]["id"]
        print(f"Using existing repository: {repo_id}")
    else:
        result = (
            sb.table("repositories")
            .insert({"name": "acme/payments", "url": "https://github.com/acme/payments"})
            .execute()
        )
        repo_id = result.data[0]["id"]
        print(f"Created repository: {repo_id}")

    # Build DocumentSource objects
    sources = [
        DocumentSource(
            content=doc["content"],
            source_type=doc["source_type"],
            title=doc["title"],
            source_path=doc["source_path"],
            repository="acme/payments",
            repository_id=repo_id,
        )
        for doc in DEMO_DOCS
    ]

    print(f"Ingesting {len(sources)} documents...")
    records = ingest_documents(sources)
    print(f"Created {len(records)} document chunks in Supabase + Qdrant")

    # Verify with a test query
    from contextsuite_agent.retrieval import retrieve_context

    results, summary = retrieve_context(
        "webhook crashes when customer email is null",
        repository_id=repo_id,
    )
    print(f"\nTest retrieval: {len(results)} results")
    print(f"Top result score: {results[0].score:.2f}" if results else "No results")
    print(f"\n{summary}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
