# ingest/loader.py
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from pathlib import Path
from typing import List
from langchain_core.documents import Document

DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data"

def load_documents(data_dir: str = None) -> List[Document]:
    """
    Load PDFs and TXTs from the data directory and return a list of LangChain Documents.
    """
    base = DATA_DIRECTORY if data_dir is None else Path(data_dir)
    docs = []

    # PDFs
    pdf_loader = DirectoryLoader(str(base), glob="**/*.pdf", loader_cls=PyPDFLoader, silent_errors=True)
    docs.extend(pdf_loader.load())

    # TXTs
    txt_loader = DirectoryLoader(str(base), glob="**/*.txt", loader_cls=TextLoader, silent_errors=True)
    docs.extend(txt_loader.load())

    return docs
if __name__ == "__main__":
    documents = load_documents()
    print(f"Loaded {len(documents)} documents.")