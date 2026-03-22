"""Test connectivity to Qdrant Cloud."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

url = os.getenv("QDRANT_URL", "")
api_key = os.getenv("QDRANT_API_KEY", "")

if not url or not api_key:
    print("[SKIP] QDRANT_URL or QDRANT_API_KEY not set in .env")
    sys.exit(0)

from qdrant_client import QdrantClient

print(f"Connecting to Qdrant: {url}")
try:
    client = QdrantClient(url=url, api_key=api_key, timeout=10)
    collections = client.get_collections()
    names = [c.name for c in collections.collections]
    print(f"  [OK] Connected. Collections: {names if names else '(none yet)'}")
except Exception as e:
    print(f"  [FAIL] {e}")
