"""SURYA AI — FastAPI entry point.

Run with:  uvicorn app.main:app --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from rag.chain import build_rag_chain, query_rag
from rag.config import STATIC_DIR
from rag.vectorstore import get_retriever, load_vectorstore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

state = {"chain": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the index and build the chain once at startup, not per request."""
    try:
        vectorstore = load_vectorstore()
        state["chain"] = build_rag_chain(get_retriever(vectorstore))
        logger.info("RAG chain ready.")
    except Exception:
        logger.exception("RAG chain unavailable — /manual-query will return 503.")
    yield
    state.clear()


app = FastAPI(title="SURYA AI", version="0.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class Query(BaseModel):
    issue: str = Field(min_length=3, max_length=2000)


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "chat_ui.html")


@app.get("/health")
def health():
    return {"status": "ok", "chain_loaded": state.get("chain") is not None}


@app.post("/manual-query")
def manual_query(query: Query):
    if state.get("chain") is None:
        raise HTTPException(
            status_code=503,
            detail="Vector index not loaded. Run: python -m scripts.ingest",
        )
    try:
        return query_rag(state["chain"], query.issue)
    except Exception:
        logger.exception("Query failed")
        raise HTTPException(status_code=500, detail="Query failed.")


@app.post("/clear-history")
def clear_history():
    # Stateless today: history lives in the browser. Kept so the UI call succeeds.
    return {"status": "cleared"}
