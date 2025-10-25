# ingest/chunker.py
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from langchain_core.documents import Document


def chunk_documents(docs: List[Document], chunk_size=1000, chunk_overlap=200) -> List[Document]:
    """
    Use RecursiveCharacterTextSplitter to split documents into chunks (keeps metadata).
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)
    return chunks

if __name__ == "__main__":
    from ingest.loader import load_documents
    documents = load_documents()
    chunked_docs = chunk_documents(documents)
    print(f"Chunked into {len(chunked_docs)} documents.")