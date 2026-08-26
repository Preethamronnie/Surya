"""One-off ingestion: read the PDF manuals, embed them, write the FAISS index.

Run with:  python -m scripts.ingest
"""

import logging

from rag.config import MANUALS_DIR, VECTORDB_DIR
from rag.loader import load_and_split_pdfs
from rag.vectorstore import create_vectorstore, save_vectorstore

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("Loading PDFs from %s ...", MANUALS_DIR)
    documents = load_and_split_pdfs(MANUALS_DIR)
    logger.info("Total chunks created: %d", len(documents))

    logger.info("Building vector index ...")
    vectorstore = create_vectorstore(documents)

    logger.info("Saving to %s ...", VECTORDB_DIR)
    save_vectorstore(vectorstore, VECTORDB_DIR)

    logger.info("Done. Vector DB is ready.")


if __name__ == "__main__":
    main()
