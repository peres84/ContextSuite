"""Document chunking for text content."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    """A chunk of text with position metadata."""

    text: str
    index: int
    total: int


def chunk_document(
    text: str,
    max_chars: int = 4000,
    overlap: int = 200,
) -> list[Chunk]:
    """Split text into overlapping chunks.

    Short documents (under max_chars) are returned as a single chunk.
    Longer documents are split on paragraph boundaries when possible,
    falling back to sentence boundaries, then hard character splits.
    """
    text = text.strip()
    if not text:
        return []

    if len(text) <= max_chars:
        return [Chunk(text=text, index=0, total=1)]

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + max_chars

        if end >= len(text):
            chunks.append(text[start:])
            break

        # Try to break at a paragraph boundary
        split_at = text.rfind("\n\n", start + (max_chars // 2), end)
        if split_at == -1:
            # Try sentence boundary
            split_at = text.rfind(". ", start + (max_chars // 2), end)
            if split_at != -1:
                split_at += 1  # include the period
        if split_at == -1:
            # Hard split at max_chars
            split_at = end

        chunk_text = text[start:split_at].rstrip()
        if chunk_text:
            chunks.append(chunk_text)
        start = max(split_at - overlap, start + 1)

    total = len(chunks)
    return [Chunk(text=c, index=i, total=total) for i, c in enumerate(chunks)]
