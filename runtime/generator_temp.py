# runtime/generator.py
import os
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

def generate_with_openai(prompt: str, max_tokens: int = 256, temperature: float = 0.2):
    import openai
    openai.api_key = OPENAI_KEY
    # use ChatCompletion for chat models
    model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[OpenAI generation error] {e}"

def generate_fallback(prompt: str):
    """
    Lightweight fallback: return a grounded summary by echoing the context header + first bytes.
    Not a replacement for an LLM, but safe and fast.
    """
    # Try to extract the "Context:" section from the prompt
    try:
        ctx = prompt.split("Context:")[1].split("Question:")[0].strip()
        excerpt = ctx[:1500]
        return "Grounded excerpt from retrieved docs:\n\n" + excerpt + ("\n\n...[truncated]" if len(ctx) > 1500 else "")
    except Exception:
        return "Could not generate a fallback answer."

def generate(prompt: str, **kwargs):
    if LLM_PROVIDER == "openai" and OPENAI_KEY:
        return generate_with_openai(prompt, **kwargs)
    else:
        return generate_fallback(prompt)
if __name__ == "__main__":
    sample_prompt = """You are a helpful assistant. Use the following context to answer the question.
If the context does not contain the answer, say "I don't know".
Context:
--- Source: doc1.txt ---
This is the content of document one.            
--- Source: doc2.txt ---
This is the content of document two.
Question:
What is the content of document one?
Answer:
"""
    answer = generate(sample_prompt, max_tokens=100)
    print("Generated answer:\n", answer)    
    
