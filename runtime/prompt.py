# runtime/prompt.py
def build_context_from_docs(docs, max_chars=3000):
    """
    Join top-k docs into a single context string limited to max_chars.
    Keeps a small source header for traceability.
    """
    parts = []
    for d in docs:
        meta = getattr(d, "metadata", {}) or {}
        src = meta.get("source") or meta.get("doc_id") or "unknown"
        header = f"--- Source: {src} ---"
        content = d.page_content if hasattr(d, "page_content") else (d.content if hasattr(d, "content") else str(d))
        parts.append(f"{header}\n{content}")
    context = "\n\n".join(parts)
    if len(context) > max_chars:
        context = context[:max_chars] + "\n\n...[truncated]"
    return context

BASE_PROMPT = """You are a helpful assistant. Use the following context to answer the question.
If the context does not contain the answer, say "I don't know".

Context:
{context}

Question:
{question}

Answer:
"""

def build_prompt(docs, question):
    ctx = build_context_from_docs(docs)
    return BASE_PROMPT.format(context=ctx, question=question)

if __name__ == "__main__":
    from langchain_core.documents import Document
    sample_docs = [
        Document(page_content="This is the content of document one.", metadata={"source": "doc1.txt"}),
        Document(page_content="This is the content of document two.", metadata={"source": "doc2.txt"}),
    ]
    question = "What is the content of document one?"
    prompt = build_prompt(sample_docs, question)
    print("promt: \n", prompt)
