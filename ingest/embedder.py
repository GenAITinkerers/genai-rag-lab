# ingest/embedder.py
import os
from langchain_community.embeddings import SentenceTransformerEmbeddings

def get_embeddings(model_name: str = None):
    """
    Return a SentenceTransformerEmbeddings instance (wraps HuggingFace sentence-transformers).
    """
    model_name = model_name or os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
    emb = SentenceTransformerEmbeddings(model_name=model_name)
    return emb

if __name__ == "__main__":
    embedding_model = get_embeddings()
    sample_text = "This is a sample text for embedding."
    embedding_vector = embedding_model.embed_query(sample_text)
    print(f"Embedding vector for sample text: {embedding_vector}")