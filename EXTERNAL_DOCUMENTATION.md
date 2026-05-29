# GenAI-RAG

A Retrieval-Augmented Generation (RAG) service that enables natural language querying over a private document corpus. Upload PDF or TXT documents, and the system will index them and return LLM-generated answers grounded in your content, with source references included in every response.

---

## Requirements

- Python 3.11 or higher
- A [HuggingFace](https://huggingface.co) account with a valid API token
- Docker (optional, for containerised deployment)

---

## Setup

**1. Prepare your documents**

Place the PDF and/or TXT files you wish to query into the `./data/` directory.

**2. Install dependencies**

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

**3. Configure environment variables**

```bash
cp tests/testenv .env
```

Edit `.env` and provide values for the following variables:

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `huggingface` | Set to `huggingface` to use the inference API, or `local` for an offline fallback |
| `HUGGINGFACEHUB_API_TOKEN` | — | Your HuggingFace API token. Required when `LLM_PROVIDER=huggingface` |
| `EMBED_MODEL` | `all-MiniLM-L6-v2` | Sentence-transformer model used to generate embeddings |
| `PERSIST_DIRECTORY` | `./today` | Directory where the vector store is persisted |
| `DATA_DIRECTORY` | `./data` | Directory from which documents are loaded |
| `COLLECTION_NAME` | `testing1` | Name of the vector store collection |

**4. Start the application**

```bash
streamlit run ui/app.py
```

The application will be available at `http://localhost:8501`.

---

## Usage

The web interface provides two operations:

**Ingest Documents**
Click the **Ingest Documents** button to load, process, and index all documents in the configured data directory. This step is required before querying and only needs to be repeated when documents are added or changed.

**Ask a Question**
Enter a question in the query field and select the number of source documents to retrieve (top-k). The system will return a generated answer along with the relevant source excerpts for verification.

---

## Docker Deployment

```bash
docker build -t genai-rag .
docker run -p 8501:8501 --env-file .env genai-rag
```

The application will be available at `http://localhost:8501`. The container exposes port `8501` and includes a health check endpoint at `/_stcore/health`.

---

## Capabilities and Limitations

| Capability | Detail |
|---|---|
| Supported document formats | PDF, TXT |
| Embedding model | `all-MiniLM-L6-v2` (configurable) |
| LLM | HuggingFace `zephyr-7b-beta` via Inference API |
| Offline fallback | Returns grounded excerpts from source documents when `LLM_PROVIDER=local` |
| Vector store | ChromaDB, persisted locally |

The system answers questions based solely on the content of indexed documents. If the answer is not present in the corpus, the model will indicate that the information is not available.

---

## Architecture Overview

The system is composed of two pipelines:

**Ingest Pipeline** — Triggered on demand via the UI. Loads documents from the data directory, splits them into chunks, generates vector embeddings, and persists them to a local ChromaDB collection.

**Query Pipeline** — Triggered per user query. Performs semantic similarity search against the vector store to retrieve the most relevant document chunks, constructs a context-grounded prompt, and returns a generated answer via the configured LLM.

```
Ingest:  Documents → Chunking → Embedding → Vector Store (disk)

Query:   Question → Similarity Search → Prompt Construction → LLM → Answer + Sources
```
