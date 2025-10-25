# ui/app.py
import sys
import streamlit as st
from dotenv import load_dotenv
import os

# Add project root to sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from ingest.loader import load_documents
from ingest.chunker import chunk_documents
from ingest.embedder import get_embeddings
from ingest.indexer import build_and_persist_vectorstore
from runtime.retriever import load_vectorstore, retrieve
from runtime.prompt import build_prompt
from runtime.generator import generate

load_dotenv()  # load .env if present

# Config (use env or defaults)
DATA_DIRECTORY = os.getenv("DATA_DIRECTORY", "./data")
PERSIST_DIRECTORY = os.getenv("PERSIST_DIRECTORY", "./today")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "testing1")
EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

st.set_page_config(page_title="RAG Streamlit App", layout="wide")
st.title("RAG App — modular version")

st.markdown("Use the **Ingest** button if you added/changed files in the `data/` folder.")

# Session-state vectorstore
if "vectordb" not in st.session_state:
    st.session_state.vectordb = None

# Ingest pipeline UI
with st.expander("1) Ingest documents (click to run)"):
    st.write(f"Data directory: `{DATA_DIRECTORY}`")
    if st.button("Ingest Documents"):
        with st.spinner("Loading documents..."):
            docs = load_documents(DATA_DIRECTORY)
            st.write(f"Loaded {len(docs)} documents.")
            if docs:
                chunks = chunk_documents(docs)
                st.write(f"Created {len(chunks)} chunks.")
                emb = get_embeddings(EMBED_MODEL)
                st.write("Embedding model ready.")
                try:
                    vectordb = build_and_persist_vectorstore(chunks, emb, PERSIST_DIRECTORY, COLLECTION_NAME)
                    st.success("Vectorstore built and persisted.")
                    st.session_state.vectordb = vectordb
                except Exception as e:
                    st.error(f"Failed to build index: {e}")
            else:
                st.warning("No documents found. Place PDFs / TXTs into the data directory.")

# Load existing store if not loaded
if st.session_state.vectordb is None:
    try:
        vect = load_vectorstore(PERSIST_DIRECTORY, COLLECTION_NAME, model_name=EMBED_MODEL)
        if vect is not None:
            st.session_state.vectordb = vect
            st.success("Loaded existing vectorstore from disk.")
        else:
            st.info("No persisted vectorstore found. Please ingest documents.")
    except Exception as e:
        st.error(f"Error loading persisted vectorstore: {e}")

# Query UI
st.markdown("---")
st.header("2) Ask a question")

col1, col2 = st.columns([4, 1])
with col1:
    question = st.text_input("Enter your question here")
with col2:
    k = st.number_input("Top-k", min_value=1, max_value=10, value=3, step=1)

if st.button("Get Answer"):
    if not st.session_state.vectordb:
        st.warning("Vectorstore not ready. Ingest documents first.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Retrieving documents..."):
            docs = retrieve(question, st.session_state.vectordb, k=k)
        if not docs:
            st.info("No relevant documents found.")
        else:
            prompt = build_prompt(docs, question)
            with st.spinner("Calling generator..."):
                answer = generate(prompt, max_tokens=300, temperature=0.2)
            st.subheader("Answer")
            st.info(answer)
            with st.expander("Retrieved documents (for traceability)"):
                for i, d in enumerate(docs):
                    meta = getattr(d, "metadata", {}) or {}
                    src = meta.get("source", meta.get("doc_id", "unknown"))
                    st.write(f"--- [{i+1}] Source: {src}")
                    content = d.page_content if hasattr(d, "page_content") else getattr(d, "content", str(d))
                    st.text(content[:1000] + ("...[truncated]" if len(content) > 1000 else ""))

st.markdown("---")
st.markdown("Small note: currently generation uses OpenAI (if configured) or a safe fallback that returns grounded excerpts.")
