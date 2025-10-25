import os
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv

load_dotenv()
LLM_PROVIDER=os.getenv("LLM_PROVIDER","huggingface")
HF_MODEL = os.getenv("HF_MODEL", "HuggingFaceH4/zephyr-7b-beta")
HF_TASK = os.getenv("HF_TASK", "text-generation")
HF_MAX_NEW_TOKENS = int(os.getenv("HF_MAX_NEW_TOKENS", "256"))

def generate_with_huggingface(prompt: str, max_tokens: int = None, temperature: float = 0.2):
    endpoint = HuggingFaceEndpoint(
        repo_id=HF_MODEL,
        task=HF_TASK,
        max_new_tokens=max_tokens or HF_MAX_NEW_TOKENS,
        temperature=temperature
    )
    model = ChatHuggingFace(llm=endpoint)
    result = model.invoke(prompt)
    return result.content

def generate_fallback(prompt: str):
    try:
        ctx = prompt.split("Context:")[1].split("Question:")[0].strip()
        excerpt = ctx[:1500]
        return "Grounded excerpt from retrieved docs:\n\n" + excerpt + ("\n\n...[truncated]" if len(ctx) > 1500 else "")
    except Exception:
        return "Could not generate a fallback answer."
    
def generate(prompt: str, **kwargs):
    if LLM_PROVIDER.lower() == "huggingface":
        print(f"LLM_PROVIDER is set to '{LLM_PROVIDER}'. Using HuggingFace model.")
        return generate_with_huggingface(prompt, **kwargs)
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