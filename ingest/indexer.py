# ingest/indexer.py
import os
from langchain_community.vectorstores import Chroma
from typing import List
from langchain_core.documents import Document

def build_and_persist_vectorstore(chunks: List[Document], embedding_function, persist_directory: str, collection_name: str):
    """
    Create Chroma vectorstore from chunked documents and persist to disk.
    """
    # simple safety check
    if not chunks:
        raise ValueError("No chunks to index.")

    # build Chroma from documents
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    vectordb.persist()
    return vectordb

if __name__ == "__main__":
    from ingest.loader import load_documents
    from ingest.chunker import chunk_documents
    from ingest.embedder import get_embeddings

    # Load and chunk documents
    documents = load_documents()
    chunked_docs = chunk_documents(documents)

    # Get embedding model
    embedding_model = get_embeddings()

    # Build and persist vectorstore
    vectordb = build_and_persist_vectorstore(
        chunks=chunked_docs,
        embedding_function=embedding_model,
        persist_directory=os.getenv("VECTORSTORE_DIR", "vectorstore"),
        collection_name="my_collection"
    )
    print("Vectorstore built and persisted.")