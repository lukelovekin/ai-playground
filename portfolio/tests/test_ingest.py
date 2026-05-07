from backend.ingest import chunk_text


class TestChunkText:
    def test_short_text_single_chunk(self):
        text = "hello world this is short"
        chunks = chunk_text(text, size=50, overlap=5)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_long_text_produces_multiple_chunks(self):
        words = ["word"] * 200
        chunks = chunk_text(" ".join(words), size=50, overlap=10)
        assert len(chunks) > 1

    def test_chunk_size_respected(self):
        words = ["word"] * 200
        chunks = chunk_text(" ".join(words), size=50, overlap=0)
        for chunk in chunks:
            assert len(chunk.split()) <= 50

    def test_overlap_produces_more_chunks_than_no_overlap(self):
        text = " ".join(["word"] * 300)
        chunks_no_overlap = chunk_text(text, size=100, overlap=0)
        chunks_with_overlap = chunk_text(text, size=100, overlap=20)
        assert len(chunks_with_overlap) >= len(chunks_no_overlap)

    def test_empty_text_returns_no_chunks(self):
        assert chunk_text("") == []
        assert chunk_text("   ") == []

    def test_no_empty_chunks(self):
        text = " ".join(["word"] * 150)
        chunks = chunk_text(text, size=50, overlap=10)
        assert all(c.strip() for c in chunks)
