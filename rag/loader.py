"""Load PDF manuals from disk and split them into retrievable chunks."""

import logging
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.config import CHUNK_OVERLAP, CHUNK_SIZE, MANUALS_DIR

logger = logging.getLogger(__name__)


def load_and_split_pdfs(folder_path=MANUALS_DIR):
    """Recursively load every PDF under folder_path and return split Documents."""
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"Manuals folder not found: {folder}")

    documents = []
    pdf_paths = sorted(folder.rglob("*.pdf"))
    if not pdf_paths:
        raise FileNotFoundError(f"No PDF files found under: {folder}")

    for path in pdf_paths:
        logger.info("Loading: %s", path.name)
        try:
            pages = PyPDFLoader(str(path)).load()
        except Exception:
            logger.exception("Skipping unreadable PDF: %s", path.name)
            continue
        # Keep a clean filename on every chunk so citations are human-readable.
        for page in pages:
            page.metadata["source"] = path.name
        documents.extend(pages)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)
