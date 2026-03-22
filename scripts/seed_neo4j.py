"""Seed Neo4j with demo graph data for acme/payments.

Usage: uv run --package contextsuite-context-agent python scripts/seed_neo4j.py

Run scripts/setup_neo4j.py first to create constraints and indexes.
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("NEO4J_URI", "")
user = os.getenv("NEO4J_USERNAME", "") or os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "")
database = os.getenv("NEO4J_DATABASE", "") or None

if not uri or not password:
    print("[SKIP] NEO4J_URI or NEO4J_PASSWORD not set")
    sys.exit(0)

from contextsuite_agent.persistence.client import get_supabase  # noqa: E402
from neo4j import GraphDatabase  # noqa: E402

sb = get_supabase()
repos = sb.table("repositories").select("id").eq("name", "acme/payments").execute()
if not repos.data:
    print("[ERROR] acme/payments not found in Supabase. Run scripts/ingest_demo.py first.")
    sys.exit(1)

REPO_ID = repos.data[0]["id"]
print(f"Repository acme/payments: {REPO_ID}")


def seed(tx):
    """Create all demo nodes and relationships in a single transaction."""

    # Repository
    tx.run(
        "MERGE (r:Repository {id: $id}) SET r.name = $name, r.url = $url",
        id=REPO_ID, name="acme/payments", url="https://github.com/acme/payments",
    )

    # Files
    files = [
        ("src/webhooks/webhook_handler.py", "python"),
        ("src/payments/charge.py", "python"),
        ("src/payments/idempotency.py", "python"),
        ("src/payments/errors.py", "python"),
        ("src/users/user_service.py", "python"),
        ("src/webhooks/stripe_events.py", "python"),
        ("src/config/settings.py", "python"),
        ("tests/test_webhooks.py", "python"),
        ("tests/test_charge.py", "python"),
    ]
    for path, lang in files:
        tx.run(
            "MERGE (f:File {id: $id}) SET f.path = $path, f.language = $lang",
            id=f"file:{path}", path=path, lang=lang,
        )
        tx.run(
            """
            MATCH (r:Repository {id: $repo_id}), (f:File {id: $file_id})
            MERGE (r)-[:HAS_FILE]->(f)
            """,
            repo_id=REPO_ID, file_id=f"file:{path}",
        )

    # Issues / Incidents
    issues = [
        {
            "id": "INC-2024-0142",
            "title": "Payment webhook crash on null email",
            "status": "resolved",
            "severity": "critical",
            "affects": ["src/webhooks/webhook_handler.py"],
        },
        {
            "id": "INC-2024-0098",
            "title": "Duplicate charge on retry storm",
            "status": "resolved",
            "severity": "high",
            "affects": ["src/payments/charge.py"],
        },
        {
            "id": "INC-2024-0201",
            "title": "Timeout in webhook handler calling user-service",
            "status": "open",
            "severity": "medium",
            "affects": [
                "src/webhooks/webhook_handler.py",
                "src/users/user_service.py",
            ],
        },
    ]
    for issue in issues:
        tx.run(
            """
            MERGE (i:Issue {id: $id})
            SET i.title = $title, i.status = $status, i.severity = $severity
            """,
            id=issue["id"], title=issue["title"],
            status=issue["status"], severity=issue["severity"],
        )
        tx.run(
            """
            MATCH (r:Repository {id: $repo_id}), (i:Issue {id: $issue_id})
            MERGE (r)-[:HAS_ISSUE]->(i)
            """,
            repo_id=REPO_ID, issue_id=issue["id"],
        )
        for fpath in issue["affects"]:
            tx.run(
                """
                MATCH (i:Issue {id: $issue_id}), (f:File {id: $file_id})
                MERGE (i)-[:AFFECTS]->(f)
                """,
                issue_id=issue["id"], file_id=f"file:{fpath}",
            )

    # Related issues
    tx.run(
        """
        MATCH (a:Issue {id: 'INC-2024-0142'}), (b:Issue {id: 'INC-2024-0201'})
        MERGE (a)-[:RELATED_TO]->(b)
        """,
    )

    # Entities (functions/classes)
    entities = [
        ("handle_payment_success", "function", "src/webhooks/webhook_handler.py"),
        ("handle_refund", "function", "src/webhooks/webhook_handler.py"),
        ("charge_customer", "function", "src/payments/charge.py"),
        ("generate_idempotency_key", "function", "src/payments/idempotency.py"),
        ("PaymentFailedError", "class", "src/payments/errors.py"),
        ("get_user_by_email", "function", "src/users/user_service.py"),
    ]
    for name, kind, fpath in entities:
        tx.run(
            "MERGE (e:Entity {id: $id}) SET e.name = $name, e.kind = $kind",
            id=f"entity:{fpath}:{name}", name=name, kind=kind,
        )
        tx.run(
            """
            MATCH (f:File {id: $file_id}), (e:Entity {id: $entity_id})
            MERGE (f)-[:DEFINES]->(e)
            """,
            file_id=f"file:{fpath}", entity_id=f"entity:{fpath}:{name}",
        )

    # Call relationships
    tx.run(
        """
        MATCH (a:Entity {name: 'handle_payment_success'}), (b:Entity {name: 'get_user_by_email'})
        MERGE (a)-[:CALLS]->(b)
        """,
    )
    tx.run(
        """
        MATCH (a:Entity {name: 'charge_customer'}), (b:Entity {name: 'generate_idempotency_key'})
        MERGE (a)-[:CALLS]->(b)
        """,
    )

    # Import relationships
    imports = [
        ("src/webhooks/webhook_handler.py", "src/users/user_service.py"),
        ("src/webhooks/webhook_handler.py", "src/payments/charge.py"),
        ("src/payments/charge.py", "src/payments/idempotency.py"),
        ("src/payments/charge.py", "src/payments/errors.py"),
        ("tests/test_webhooks.py", "src/webhooks/webhook_handler.py"),
        ("tests/test_charge.py", "src/payments/charge.py"),
    ]
    for src, dst in imports:
        tx.run(
            """
            MATCH (a:File {id: $src_id}), (b:File {id: $dst_id})
            MERGE (a)-[:IMPORTS]->(b)
            """,
            src_id=f"file:{src}", dst_id=f"file:{dst}",
        )

    # Constraints
    constraints = [
        {
            "id": "constraint:no-user-svc-in-webhooks",
            "description": "Webhook handlers must not call user-service synchronously",
            "source": "Architecture Review Board, 2024-09",
        },
        {
            "id": "constraint:webhook-5s-timeout",
            "description": "All webhook handlers must complete within 5 seconds",
            "source": "ADR-012",
        },
        {
            "id": "constraint:currency-in-cents",
            "description": "All monetary values stored as integer cents (ADR-007)",
            "source": "ADR-007",
        },
    ]
    for c in constraints:
        tx.run(
            """
            MERGE (c:Constraint {id: $id})
            SET c.description = $desc, c.source = $source
            """,
            id=c["id"], desc=c["description"], source=c["source"],
        )
        tx.run(
            """
            MATCH (c:Constraint {id: $cid}), (r:Repository {id: $repo_id})
            MERGE (c)-[:APPLIES_TO]->(r)
            """,
            cid=c["id"], repo_id=REPO_ID,
        )

    # Constraint applies to specific files too
    tx.run(
        """
        MATCH (c:Constraint {id: 'constraint:no-user-svc-in-webhooks'}),
              (f:File {id: 'file:src/webhooks/webhook_handler.py'})
        MERGE (c)-[:APPLIES_TO]->(f)
        """,
    )


def main():
    print(f"Connecting to Neo4j: {uri}")
    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session(database=database) as session:
        # Verify connection
        session.run("RETURN 1").single()
        print("  [OK] Connected")

        # Seed data
        print("  Seeding graph data...")
        session.execute_write(seed)
        print("  [OK] Seed complete")

        # Verify
        result = session.run("MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count")
        print("\n  Node counts:")
        for rec in result:
            print(f"    {rec['label']}: {rec['count']}")

        result = session.run("MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count")
        print("\n  Relationship counts:")
        for rec in result:
            print(f"    {rec['type']}: {rec['count']}")

    driver.close()
    print("\n  [OK] Neo4j seeded successfully")


if __name__ == "__main__":
    main()
