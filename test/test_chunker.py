import pytest
from langchain_core.documents import Document
from ingest.chunker import chunk_documents


def make_doc(text, source="test.txt"):
    return Document(page_content=text, metadata={"source": source})


def test_returns_list_of_documents():
    docs = [make_doc("Hello world.")]
    chunks = chunk_documents(docs)
    assert isinstance(chunks, list)
    assert all(isinstance(c, Document) for c in chunks)


def test_short_doc_produces_single_chunk():
    docs = [make_doc("Short text.")]
    chunks = chunk_documents(docs)
    assert len(chunks) == 1
    assert chunks[0].page_content == "Short text."


def test_long_doc_is_split():
    long_text = "word " * 400  # ~2000 chars, exceeds default chunk_size=1000
    docs = [make_doc(long_text)]
    chunks = chunk_documents(docs)
    assert len(chunks) > 1


def test_chunks_respect_chunk_size():
    long_text = "a" * 3000
    chunks = chunk_documents([make_doc(long_text)], chunk_size=500, chunk_overlap=0)
    for chunk in chunks:
        assert len(chunk.page_content) <= 500


def test_overlap_produces_shared_content():
    # With overlap, adjacent chunks should share some characters
    text = "a" * 1000
    chunks = chunk_documents([make_doc(text)], chunk_size=200, chunk_overlap=50)
    assert len(chunks) > 1
    # end of chunk[0] should appear at start of chunk[1]
    end_of_first = chunks[0].page_content[-50:]
    assert chunks[1].page_content.startswith(end_of_first)


def test_metadata_is_preserved():
    docs = [make_doc("Some content.", source="myfile.pdf")]
    chunks = chunk_documents(docs)
    assert all(c.metadata.get("source") == "myfile.pdf" for c in chunks)


def test_multiple_docs_are_all_chunked():
    docs = [make_doc(f"Document {i} content.") for i in range(3)]
    chunks = chunk_documents(docs)
    assert len(chunks) >= 3


def test_empty_input_returns_empty_list():
    assert chunk_documents([]) == []


def test_custom_chunk_size_and_overlap():
    text = "x" * 500
    chunks = chunk_documents([make_doc(text)], chunk_size=100, chunk_overlap=10)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.page_content) <= 100
