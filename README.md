# SURYA AI

Retrieval-augmented Q&A over FIMER PVS980-58 solar inverter manuals. Ask a field
question in plain English, get an answer grounded in the manual text with page
citations.

FastAPI backend + FAISS vector store + local HuggingFace embeddings + OpenAI for
generation.

## Layout

```
app/main.py          FastAPI app — serves the UI and the /manual-query endpoint
rag/config.py        All paths and tunables (chunk size, k, model names)
rag/loader.py        PDF loading + chunking
rag/embedder.py      Embedding model factory (cached)
rag/vectorstore.py   FAISS create / save / load / retriever
rag/chain.py         RetrievalQA chain + grounded prompt
scripts/ingest.py    One-off: build the vector index from data/manuals/
static/chat_ui.html  Chat front end
data/manuals/        Source PDFs (gitignored)
data/vectordb/       Generated FAISS index (gitignored)
legacy/              Original ungrouped code fragments, kept for reference
docs/                Reference material (PDFs gitignored)
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

copy .env.example .env          # then paste your OpenAI key into .env
```

## Build the index

Drop the manual PDFs into `data/manuals/`, then:

```bash
python -m scripts.ingest
```

This runs once. Re-run it whenever the manuals change.

## Run

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

## Endpoints

| Method | Path            | Purpose                                  |
|--------|-----------------|------------------------------------------|
| GET    | `/`             | Chat UI                                  |
| GET    | `/health`       | Liveness + whether the index is loaded   |
| POST   | `/manual-query` | `{"issue": "..."}` → answer + sources    |
| POST   | `/clear-history`| No-op today; history is browser-side     |

## Notes

- `data/manuals/` and `data/vectordb/` are gitignored. The manuals are FIMER
  proprietary material and the index is large and regenerable.
- Never commit `.env`. `.env.example` documents the required variables.
- `load_vectorstore` uses `allow_dangerous_deserialization=True`, which is safe
  only because the index is built locally. Do not point it at a downloaded index.

## Status

Prototype. See `docs/CODE_REVIEW.md` for known gaps and the improvement backlog.
