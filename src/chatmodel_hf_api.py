from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv

load_dotenv()
# from config import set_environment
# set_environment()

#llm = HuggingFaceEndpoint(
#    repo_id="HuggingFaceH4/zephyr-7b-beta",
#    task="text-generation",
#    max_new_tokens=20
#)

#model = ChatHuggingFace(llm=llm)

#result = model.invoke("What is the capital of India?")

#print(result.content)
llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    task="text-generation",
    max_new_tokens=20
)


if __name__ == "__main__":
    model = ChatHuggingFace(llm=llm)
    result = model.invoke("What is the capital of India?")
    print(result.content)
