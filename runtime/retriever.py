# runtime/retriever.py
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import os

def load_vectorstore(persist_directory: str, collection_name: str, model_name: str = None):
    """
    Load existing Chroma vectorstore from disk. Returns Chroma instance or None.
    """
    model_name = model_name or os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
    emb = SentenceTransformerEmbeddings(model_name=model_name)
    if not os.path.exists(persist_directory) or not any(os.scandir(persist_directory)):
        return None
    return Chroma(persist_directory=persist_directory, embedding_function=emb, collection_name=collection_name)

def retrieve(query: str, vectordb, k: int = 3):
    """
    Simple semantic search wrapper.
    Returns list of Documents (langchain schema objects).
    """
    if vectordb is None:
        return []
    docs = vectordb.similarity_search(query, k=k)
    return docs
if __name__ == "__main__":
    persist_dir = os.getenv("PERSIST_DIRECTORY", "vectorstore")
    collection_name = "my_collection"
    # Load vectorstore
    loaded_vectordb = load_vectorstore(persist_directory=persist_dir, collection_name=collection_name)

    # Test retrieval
    query = "Sample query text"
    results = retrieve(query, loaded_vectordb, k=2)
    print(f"Retrieved {len(results)} documents for query: '{query}'")
