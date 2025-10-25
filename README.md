# Genai-rag-lab

GenAI and RAG

**Project structure**

rag-streamlit/
├─ data/                          # put your PDFs/TXTs here
├─ ingest/
│  ├─ __init__.py
│  ├─ loader.py
│  ├─ chunker.py
│  ├─ embedder.py
│  └─ indexer.py
├─ runtime/
│  ├─ __init__.py
│  ├─ retriever.py
│  ├─ prompt.py
│  └─ generator.py
├─ ui/
│  ├─ __init__.py
│  └─ app.py

|--tests/

|   |---testenv
├─ .env.example
├─ requirements.txt
├─ Dockerfile
└─ README.md

# How to run locally (step-by-step)

1. copy the content, pdf, txt and file in folder ./data
2. Create virtual environment and install:

<pre class="overflow-visible!" data-start="13399" data-end="13515"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>python -m venv .venv
</span><span>source</span><span> .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
</span></span></code></div></div></pre>

3. Copy testenv to `.env` and populate it with HUGGINGFACEHUB_API_TOKEN:
5. Start Streamlit:

<pre class="overflow-visible!" data-start="13695" data-end="13730"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>streamlit run ui/app.py
</span></span></code></div></div></pre>


5. Workflow:

* Click **Ingest Documents** (this loads & chunks & builds the Chroma DB in `PERSIST_DIRECTORY`).
* Ask questions — top-k results will be retrieved and you’ll see an LLM answer (if OpenAI configured) or a grounded excerpt fallback.
