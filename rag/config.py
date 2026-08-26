"""Central configuration. All paths and tunables live here, not scattered in modules."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- Paths (absolute, so scripts work from any working directory) ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MANUALS_DIR = Path(os.getenv("MANUALS_DIR", DATA_DIR / "manuals"))
VECTORDB_DIR = Path(os.getenv("VECTORDB_DIR", DATA_DIR / "vectordb"))
STATIC_DIR = BASE_DIR / "static"

# --- Chunking ---
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

# --- Embeddings ---
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# --- Retrieval ---
RETRIEVER_K = int(os.getenv("RETRIEVER_K", 5))

# --- LLM ---
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
