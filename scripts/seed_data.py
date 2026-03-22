"""Seed demo data into Supabase and Qdrant for development.

Creates:
- 1 demo repository
- Sample context documents embedded in Qdrant
"""

import os
import sys
import uuid

from dotenv import load_dotenv

load_dotenv()

# Check required env vars
if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
    print("[SKIP] Supabase credentials not set")
    sys.exit(0)

from google import genai
from qdrant_client.models import PointStruct
from supabase import create_client

# --- Supabase seed ---

print("=== Seeding Supabase ===")
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

# Check if demo repo already exists
existing = sb.table("repositories").select("id").eq("name", "acme/payments").execute()
if existing.data:
    repo_id = existing.data[0]["id"]
    print(f"  Demo repo already exists: {repo_id}")
else:
    result = sb.table("repositories").insert({
        "name": "acme/payments",
        "url": "https://github.com/acme/payments",
        "description": "Payment processing service — the demo target repository",
    }).execute()
    repo_id = result.data[0]["id"]
    print(f"  Created demo repo: {repo_id}")

print(f"  Repository ID: {repo_id}")

# --- Qdrant seed ---

print()
print("=== Seeding Qdrant ===")

qdrant_url = os.getenv("QDRANT_URL", "")
qdrant_key = os.getenv("QDRANT_API_KEY", "")
google_key = os.getenv("GOOGLE_API_KEY", "")
collection = os.getenv("QDRANT_COLLECTION", "contextsuite")

if not qdrant_url or not qdrant_key or not google_key:
    print("  [SKIP] Qdrant or Google API credentials not set")
    sys.exit(0)

from qdrant_client import QdrantClient

qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_key)
genai_client = genai.Client(api_key=google_key)
model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-2-preview")

# Sample context documents representing project memory
DEMO_DOCS = [
    {
        "content": "Bug: Payment webhook handler crashes when Stripe sends a charge.refunded event with a null receipt_email. Fixed by adding null check in webhook_handler.py line 142. Root cause: Stripe API changed to allow null email on guest checkouts.",
        "type": "incident",
        "file": "src/webhooks/webhook_handler.py",
    },
    {
        "content": "Architecture decision: All payment amounts must be stored in cents (integer) to avoid floating-point rounding errors. Never store currency as float or decimal. This applies to all database columns and API responses.",
        "type": "adr",
        "file": "docs/adr/003-currency-in-cents.md",
    },
    {
        "content": "Constraint: The payments service must not make direct database writes to the users table. All user updates must go through the user-service API. This was agreed after an incident where a payment migration corrupted user records.",
        "type": "constraint",
        "file": "docs/constraints.md",
    },
    {
        "content": "Bug: Duplicate charge created when customer double-clicks the pay button. Fixed by adding idempotency key based on cart_id + session_id. The Stripe API accepts an Idempotency-Key header that prevents duplicate charges.",
        "type": "incident",
        "file": "src/checkout/charge.py",
    },
    {
        "content": "The retry logic for failed webhook deliveries uses exponential backoff with jitter. Max retries: 5. Base delay: 1 second. Max delay: 60 seconds. After exhausting retries, the event is written to a dead letter queue in Supabase.",
        "type": "doc",
        "file": "src/webhooks/retry.py",
    },
]

print(f"  Embedding {len(DEMO_DOCS)} documents...")
texts = [d["content"] for d in DEMO_DOCS]
result = genai_client.models.embed_content(model=model, contents=texts)
embeddings = [e.values for e in result.embeddings]
print(f"  Got {len(embeddings)} embeddings (dim={len(embeddings[0])})")

points = []
for i, (doc, embedding) in enumerate(zip(DEMO_DOCS, embeddings)):
    points.append(
        PointStruct(
            id=uuid.uuid4().hex,
            vector=embedding,
            payload={
                "content": doc["content"],
                "type": doc["type"],
                "file": doc["file"],
                "repository": "acme/payments",
                "repository_id": repo_id,
            },
        )
    )

qdrant.upsert(collection_name=collection, points=points)
info = qdrant.get_collection(collection)
print(f"  Upserted {len(points)} points. Total in collection: {info.points_count}")

print()
print("=== Seed complete ===")
print(f"  Supabase: 1 repository (acme/payments)")
print(f"  Qdrant: {len(points)} context documents embedded")
print(f"  Neo4j: run scripts/setup_neo4j.py separately when instance is live")
