"""Test Gemini Embedding 2 multimodal endpoint."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY", "")
model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-2-preview")

if not api_key:
    print("[SKIP] GOOGLE_API_KEY not set in .env")
    sys.exit(0)

from google import genai

print(f"Testing Gemini embedding: {model}")
try:
    client = genai.Client(api_key=api_key)
    result = client.models.embed_content(
        model=model,
        contents="ContextSuite test embedding",
    )
    embedding = result.embeddings[0].values
    print(f"  [OK] Got embedding vector (dim={len(embedding)})")
    print(f"       First 5 values: {embedding[:5]}")
except Exception as e:
    print(f"  [FAIL] {e}")
