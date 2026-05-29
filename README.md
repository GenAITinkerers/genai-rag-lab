# GenAI-RAG

A Retrieval-Augmented Generation (RAG) application. Load your own PDF or TXT documents, index them into a vector store, then ask questions in natural language and get LLM-generated answers grounded in your documents — with full source traceability.

---

## Main Features

- **Document ingestion** — loads PDFs and TXT files, chunks them, embeds and persists to a vector store
- **Semantic search** — retrieves the top-k most relevant chunks for any user query
- **Answer generation** — sends retrieved context + question to an LLM; returns the answer plus the source documents
- **Streamlit UI** — single-page web app with ingest and query sections
- **Docker support** — containerized, exposes port 8501 with health checks

## Tech Stack

| Layer         | Technology                                                            |
| ------------- | --------------------------------------------------------------------- |
| UI            | Streamlit                                                             |
| Orchestration | LangChain                                                             |
| Embeddings    | `sentence-transformers` (`all-MiniLM-L6-v2`)                      |
| Vector store  | ChromaDB (persisted to `./today/`)                                  |
| LLM           | HuggingFace Inference API (`zephyr-7b-beta`), with a local fallback |
| Runtime       | Python 3.11+                                                          |

---

## Prerequisites

- Python 3.11 or higher
- A [HuggingFace account](https://huggingface.co) with an API token (required for LLM inference)

---

## Local Setup

**1. Add your documents**

Place PDF or TXT files into the `./data/` directory. These are the files the app will index and answer questions about.

**2. Create a virtual environment and install dependencies**

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

Then open `.env` and set your `HUGGINGFACEHUB_API_TOKEN`. All available variables:

| Variable                     | Default              | Description                                              |
| ---------------------------- | -------------------- | -------------------------------------------------------- |
| `LLM_PROVIDER`             | `huggingface`      | `huggingface` or `local` (grounded-excerpt fallback) |
| `HUGGINGFACEHUB_API_TOKEN` | —                   | Required for HuggingFace inference                       |
| `EMBED_MODEL`              | `all-MiniLM-L6-v2` | Sentence-transformer model name                          |
| `PERSIST_DIRECTORY`        | `./today`          | Where ChromaDB is stored on disk                         |
| `DATA_DIRECTORY`           | `./data`           | Where input documents are read from                      |
| `COLLECTION_NAME`          | `testing1`         | ChromaDB collection name                                 |

**4. Start the app**

```bash
streamlit run ui/app.py
```

- Click **Ingest Documents** to load, chunk, embed, and persist your documents to ChromaDB.
- Type a question and click **Get Answer** — the app retrieves the top-k relevant chunks and generates an answer.
- The persisted vector store is reloaded automatically on restart, so you only need to re-ingest when documents change.

---

## Docker

```bash
docker build -t genai-rag .
docker run -p 8501:8501 --env-file .env genai-rag
```

Open `http://localhost:8501` in your browser.

---

## Running Tests

```bash
pip install pytest
pytest tests/
```

---

## Architecture

The project uses a **flat functional pipeline** split across two paths: **Ingest** and **Query**. `ui/app.py` is the sole orchestrator; all other modules are stateless service functions.

### Modules

| Module                      | File                     | Role                                                                               |
| --------------------------- | ------------------------ | ---------------------------------------------------------------------------------- |
| **UI / Orchestrator** | `ui/app.py`            | Entry point. Drives both pipelines, holds vectorstore in session state             |
| **Loader**            | `ingest/loader.py`     | Reads PDFs and TXTs from `./data` via LangChain `DirectoryLoader`              |
| **Chunker**           | `ingest/chunker.py`    | Splits `Document` objects into overlapping text chunks                           |
| **Embedder**          | `ingest/embedder.py`   | Returns a `SentenceTransformerEmbeddings` model instance                         |
| **Indexer**           | `ingest/indexer.py`    | Builds a Chroma collection from chunks + embeddings, persists to disk              |
| **Retriever**         | `runtime/retriever.py` | Loads persisted Chroma store; runs `similarity_search` against a query           |
| **Prompt Builder**    | `runtime/prompt.py`    | Assembles retrieved docs + question into a structured LLM prompt string            |
| **Generator**         | `runtime/generator.py` | Calls HuggingFace Inference API (`zephyr-7b-beta`) or returns a fallback excerpt |

### Data Flow

#### Ingest Pipeline

```
[./data/ files]
      │  PDF / TXT
      ▼
  loader.py → load_documents()
      │  List[Document]
      ▼
  chunker.py → chunk_documents()
      │  List[Document] (chunks, 1000 chars / 200 overlap)
      ▼
  embedder.py → get_embeddings()
      │  SentenceTransformerEmbeddings model
      ▼
  indexer.py → build_and_persist_vectorstore()
      │  Chroma collection
      ▼
  [./today/ — persisted to disk]
      │
      └─► st.session_state.vectordb
```

#### Query Pipeline

```
[User question + top-k]
      │
      ▼
  retriever.py → retrieve()
      │  top-k List[Document] (similarity search)
      ▼
  prompt.py → build_prompt()
      │  formatted string: context + question
      ▼
  generator.py → generate()
      │  LLM_PROVIDER == "huggingface" → ChatHuggingFace (zephyr-7b-beta)
      │  else                          → generate_fallback() (raw excerpt)
      ▼
  [Answer text + source docs displayed in Streamlit]
```

### Key Design Notes

- **State boundary**: The only stateful object is `st.session_state.vectordb`. On app startup, `retriever.load_vectorstore()` tries to reload it from disk automatically — ingest is not required on every restart.
- **No abstractions/interfaces**: Every module exposes plain functions, not classes. `ui/app.py` imports and calls them directly.
- **LLM provider is runtime-switched**: `generator.py` reads `LLM_PROVIDER` from env at module load time — `"huggingface"` calls the API; anything else triggers the safe fallback.
- **Prompt is not a template engine**: `prompt.py` builds a plain f-string with a 3000-char context cap and source headers for traceability.

---

## Refactoring Prompts

Prompts for future refactoring tasks. Use these directly with an AI assistant or as task descriptions.

### General Code Quality

- *"Review all modules in `ingest/` and `runtime/` for code duplication. Suggest or apply consolidations."*
- *"Identify any functions longer than 20 lines and refactor them into smaller, single-responsibility functions."*
- *"Remove all `if __name__ == '__main__'` blocks from the ingest and runtime modules — they are development scaffolding, not production code."*

### Error Handling

- *"Add proper error handling to `ingest/loader.py` so that a single unreadable file does not silently fail or crash the entire ingestion run."*
- *"Refactor `runtime/generator.py` to raise a specific exception instead of silently falling back when the HuggingFace API call fails, and let `ui/app.py` decide how to handle it."*

### Configuration

- *"Centralise all `os.getenv()` calls into a single `config.py` module at the project root. All other modules should import from it instead of reading env vars directly."*
- *"The embedding model is initialised in both `ingest/embedder.py` and `runtime/retriever.py` independently. Refactor so the embedding model is created once and passed in as a dependency."*

### Type Safety

- *"Add type hints to all public functions across `ingest/` and `runtime/`. Use `List`, `Optional`, and return types consistently."*
- *"Add a `py.typed` marker and verify that the codebase passes `mypy --strict` with no errors."*

### Testing

- *"Write unit tests for `runtime/prompt.py` covering: context truncation at 3000 chars, missing metadata fields, and multi-document formatting."*
- *"Write unit tests for `runtime/generator.py` that mock the HuggingFace endpoint so tests do not make real API calls."*
- *"Refactor `tests/test_chunker.py` to use `pytest.mark.parametrize` for the chunk size and overlap test cases."*

### Dependencies & Imports

- *"`requirements.txt` includes `openai` and `PyPDF2` which appear unused. Audit all imports across the project and remove any unused dependencies from `requirements.txt`."*
- *"Replace the deprecated `langchain_community.vectorstores.Chroma` import with the current `langchain_chroma` package."*

### Docker & Deployment

- *"The Dockerfile copies `./today/` (the vector store) into the image. Refactor so the container reads the vector store from a mounted volume instead, keeping the image stateless."*
