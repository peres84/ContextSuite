# Qdrant Schema

## Collection: `contextsuite`

| Property | Value |
|---|---|
| Vector dimensions | 3072 |
| Distance metric | Cosine |
| Embedding model | Gemini Embedding 2 (`models/gemini-embedding-2-preview`) |

## Point Payload Schema

Each point in the collection has the following payload fields:

| Field | Type | Description |
|---|---|---|
| content | string | The original text that was embedded |
| type | string | Document type: `incident`, `adr`, `constraint`, `doc`, `code_summary` |
| file | string | Source file path (e.g., `src/webhooks/webhook_handler.py`) |
| repository | string | Repository name (e.g., `acme/payments`) |
| repository_id | string | UUID of the repository in Supabase |

## Recovery

To recreate the collection:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

client.create_collection(
    collection_name="contextsuite",
    vectors_config=VectorParams(
        size=3072,
        distance=Distance.COSINE,
    ),
)
```

To re-seed demo data:

```bash
uv run python scripts/seed_data.py
```
