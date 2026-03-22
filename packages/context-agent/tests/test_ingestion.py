"""Tests for the ingestion pipeline components."""

from contextsuite_agent.ingestion.chunker import Chunk, chunk_document
from contextsuite_agent.ingestion.sources import DocumentSource, SourceType


class TestChunker:
    def test_empty_text(self):
        assert chunk_document("") == []
        assert chunk_document("   ") == []

    def test_short_text_single_chunk(self):
        text = "This is a short document."
        chunks = chunk_document(text)
        assert len(chunks) == 1
        assert chunks[0].text == text
        assert chunks[0].index == 0
        assert chunks[0].total == 1

    def test_long_text_multiple_chunks(self):
        # Create text longer than max_chars
        text = "Paragraph one. " * 100 + "\n\n" + "Paragraph two. " * 100
        chunks = chunk_document(text, max_chars=500)
        assert len(chunks) > 1
        for i, chunk in enumerate(chunks):
            assert chunk.index == i
            assert chunk.total == len(chunks)
            assert len(chunk.text) > 0

    def test_respects_max_chars(self):
        text = "Word " * 2000
        chunks = chunk_document(text, max_chars=500, overlap=50)
        for chunk in chunks:
            assert len(chunk.text) <= 500 + 50  # allow small overflow from boundary search

    def test_paragraph_boundary_split(self):
        p1 = "A" * 300
        p2 = "B" * 300
        text = f"{p1}\n\n{p2}"
        chunks = chunk_document(text, max_chars=500, overlap=0)
        assert len(chunks) == 2
        assert chunks[0].text.strip().startswith("A")
        # With no overlap, second chunk starts right after the split
        assert "B" in chunks[1].text

    def test_chunk_dataclass(self):
        c = Chunk(text="hello", index=0, total=1)
        assert c.text == "hello"
        assert c.index == 0
        assert c.total == 1


class TestDocumentSource:
    def test_minimal_source(self):
        src = DocumentSource(content="test", source_type=SourceType.DOC)
        assert src.content == "test"
        assert src.source_type == SourceType.DOC
        assert src.title is None
        assert src.repository_id is None

    def test_full_source(self):
        src = DocumentSource(
            content="incident report",
            source_type=SourceType.INCIDENT,
            title="INC-001",
            source_path="incidents/inc-001.md",
            repository="acme/payments",
            repository_id="abc123",
            metadata={"severity": "high"},
        )
        assert src.title == "INC-001"
        assert src.metadata == {"severity": "high"}

    def test_all_source_types(self):
        for st in SourceType:
            src = DocumentSource(content="x", source_type=st)
            assert src.source_type == st
