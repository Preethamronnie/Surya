"""FAISS vector store: create, persist, load."""

from pathlib import Path

from langchain_community.vectorstores import FAISS

from rag.config import VECTORDB_DIR
from rag.embedder import get_embeddings


def create_vectorstore(documents):
    return FAISS.from_documents(documents, get_embeddings())


def save_vectorstore(vectorstore, path=VECTORDB_DIR):
    Path(path).mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(path))


def load_vectorstore(path=VECTORDB_DIR):
    path = Path(path)
    if not (path / "index.faiss").exists():
        raise FileNotFoundError(
            f"No vector index at {path}. Run:  python -m scripts.ingest"
        )
    # allow_dangerous_deserialization is safe only because we build this index
    # ourselves. Never point this at an index downloaded from elsewhere.
    return FAISS.load_local(
        str(path), get_embeddings(), allow_dangerous_deserialization=True
    )


def get_retriever(vectorstore, k=None):
    from rag.config import RETRIEVER_K

    return vectorstore.as_retriever(search_kwargs={"k": k or RETRIEVER_K})
