"""Embedding model factory. Cached so the model is loaded into memory only once."""

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from rag.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )
