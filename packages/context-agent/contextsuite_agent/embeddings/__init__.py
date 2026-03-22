"""Gemini Embedding 2 integration."""

from google import genai

from contextsuite_agent.config import settings

_client: genai.Client | None = None


def get_genai() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.google_api_key)
    return _client


def embed_text(text: str) -> list[float]:
    """Generate an embedding vector for a single text."""
    result = get_genai().models.embed_content(
        model=settings.gemini_embedding_model,
        contents=text,
    )
    return result.embeddings[0].values


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embedding vectors for multiple texts."""
    result = get_genai().models.embed_content(
        model=settings.gemini_embedding_model,
        contents=texts,
    )
    return [e.values for e in result.embeddings]
