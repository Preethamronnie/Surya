# SURYA AI — Code Review

Reviewed: 26 Aug 2026. Scope: the eight code fragments in the Surya folder plus
`chat_ui.html`, now restructured into `app/`, `rag/`, `scripts/`, `static/`.

## Verdict

The RAG design is sound — the standard load → chunk → embed → FAISS → retrieve →
generate pipeline, with a sensible split between a free local embedding model and
a paid LLM only at generation time. The problems were structural rather than
conceptual: nothing was a real Python package, imports contradicted each other,
and the front end called endpoints the backend never defined.

That is now fixed. What follows is what to do next.

---

## Fixed during restructuring

| Issue | Was | Now |
|---|---|---|
| Files not runnable | Code saved as `.txt` with the first line as the filename | Real modules: `rag/loader.py`, `rag/vectorstore.py`, etc. |
| Contradictory imports | Two ingest scripts, one `from loader import`, one `from rag.loader import` | Single `scripts/ingest.py`, package-absolute imports throughout |
| Broken import | `vectorstore.py` did `from embedder import get_embeddings` — fails outside the same directory | `from rag.embedder import get_embeddings` |
| Relative paths | `"data/manuals"` breaks if you run from anywhere but the project root | Absolute paths derived from `__file__` in `rag/config.py` |
| Dead UI | `chat_ui.html` posts to `/manual-query` and `/clear-history`; the API only had `GET /` | Both endpoints implemented; UI served at `/` |
| Chain rebuilt per call | No wiring existed | Index + chain built once at startup via FastAPI lifespan |
| Nothing gitignored | — | `.env`, `data/manuals/`, `data/vectordb/`, `docs/*.pdf` excluded |

---

## High priority

### 1. Chunk size was far too small for technical manuals

`chunk_size=500, chunk_overlap=100` was the original setting. 500 characters is
roughly 80 words — smaller than a single fault-code table row in a PVS980 manual.
A retrieved chunk would routinely contain the fault number but not its
description, threshold, and reaction.

Raised to `1000 / 200` in `rag/config.py`. Tune from there: for dense
tabular manual content, 1200–1500 with 15–20% overlap usually retrieves better.
Test with real questions before settling.

### 2. `k=3` retrieval is too narrow

Three chunks is thin when an answer spans a fault description, a parameter table,
and a troubleshooting step in different parts of the manual. Raised to 5.

Bigger win: switch to **MMR** retrieval so the five chunks aren't near-duplicates
of the same page.

```python
vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.5},
)
```

### 3. No prompt meant no grounding guarantee

`RetrievalQA.from_chain_type` with no `chain_type_kwargs` uses LangChain's generic
default prompt. For inverter troubleshooting, a hallucinated fault threshold or
torque value is worse than no answer. A domain prompt is now in `rag/chain.py`
instructing the model to answer only from the excerpts and to say so when the
manual doesn't cover it.

Verify this actually holds — ask it something deliberately absent from the manuals
and check that it declines rather than inventing.

### 4. `os.listdir` missed subfolders and silently skipped nothing

The original loader listed one flat directory and would crash the whole ingest on
a single malformed PDF. Now uses `rglob("*.pdf")` (picks up subfolders), logs and
skips unreadable files, and raises clearly if the folder is empty or missing.

### 5. Page numbers were being thrown away

`query_rag` returned only `doc.metadata.get("source")` — a full file path, often
duplicated across the three chunks. For a service engineer, "page 214 of the
PVS980-58 hardware manual" is the useful part. Sources now return
`{"source": filename, "page": n}` and are de-duplicated.

Note the front end currently only renders the answer text — wire the sources
array into `chat_ui.html` so citations are visible.

---

## Medium priority

### 6. Embedding model is the weakest link for this domain

`all-MiniLM-L6-v2` is 384-dimensional, fast, and generic. It was trained on
general web text, not electrical engineering. Terms like "MIRU", "BAMU", "gate
driver", "LCL filter" carry little signal for it.

Options, cheapest first:

- **`BAAI/bge-base-en-v1.5`** — still local and free, 768-dim, meaningfully better
  on technical retrieval. Drop-in via the same `HuggingFaceEmbeddings` call.
- **`text-embedding-3-large`** (OpenAI) — best quality, costs money per ingest,
  but ingest is a one-off so the total is small.

Whichever you pick, **the index must be rebuilt** — you cannot mix embedding
models in one FAISS index.

### 7. Hybrid retrieval would fix exact-code lookups

Dense embeddings are bad at exact-token matching. A query for fault **9107** may
retrieve chunks about 9106 and 9108 because they're semantically near-identical.
Combine BM25 keyword search with the vector search:

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

ensemble = EnsembleRetriever(
    retrievers=[BM25Retriever.from_documents(docs), vector_retriever],
    weights=[0.4, 0.6],
)
```

For a fault-code assistant this is probably the single highest-value upgrade
after chunk sizing.

### 8. No conversation memory

`RetrievalQA` is stateless. "What causes it?" as a follow-up retrieves against
those three words alone. Use `ConversationalRetrievalChain`, or the LCEL
equivalent with a history-aware retriever, so follow-ups get rewritten into
standalone queries before retrieval.

### 9. Blocking calls in an async framework

FastAPI's `def` (non-async) endpoints run in a threadpool, so this is survivable
today. But `query_rag` blocks for several seconds on the OpenAI call. Under any
real concurrency, switch to `async def` with `ainvoke`, and stream tokens back so
the UI doesn't sit silent for 5+ seconds.

### 10. No tests, no CI

Even three tests would catch the class of breakage seen here: one that imports
every module, one that chunks a fixture PDF and asserts chunk count and metadata,
one that hits `/health`. Add `pytest` and a minimal GitHub Actions workflow that
runs `python -m compileall` plus the tests on push.

---

## Lower priority / hygiene

- **Pin dependencies.** `requirements.txt` uses `>=`. Once it works, freeze exact
  versions (`pip freeze > requirements.txt`) — LangChain's API moves fast and an
  unpinned install will break this repo within months.
- **No rate limiting or auth** on `/manual-query`. Fine on localhost. Before this
  goes on any shared network, add an API key header and a request cap, or your
  OpenAI spend is open to anyone who can reach the port.
- **No CORS config.** Currently unnecessary since the UI is served same-origin.
  Only add `CORSMiddleware` if you split the front end out — and don't use
  `allow_origins=["*"]` when you do.
- **`print` → `logging`** — done, but keep it that way. Logging gives you levels
  and timestamps when you're debugging an ingest over 200 PDFs.
- **Incremental ingest.** Right now re-ingesting rebuilds everything from zero. If
  the manual set grows, hash each file and only re-embed what changed.
- **`legacy/` folder.** Kept so nothing is lost. Delete it once you've confirmed
  the new structure works — it's dead weight in the repo history otherwise.

---

## Suggested order of work

1. Rebuild the index with the new chunk settings, run five real field questions,
   judge the answers. *(No code change — just validates the defaults.)*
2. Wire the `sources` array into `chat_ui.html`. Citations are what make this
   trustworthy for RCA work.
3. Add BM25 hybrid retrieval. Test specifically on fault-code queries.
4. Swap in `bge-base-en-v1.5`, rebuild, compare against step 1's answers.
5. Add conversational memory.
6. Pin dependencies, add the three tests, add CI.

---

## One structural thought

You already maintain a curated knowledge base — `RCA Reference Memory/*.md`,
`Confirmed_Field_Failures_Master.md`, the firmware module reference. That material
is denser and better organised than the raw manuals, and it is already in Markdown,
which chunks far more cleanly than PDF.

Ingesting those alongside the manuals — with a metadata tag distinguishing
`manual` from `field_case` — would likely improve answer quality more than any of
the retrieval tuning above. A question like "why did 9107 repeat after the MIRU
self-test" is answered by your notes, not by the manual.

Worth considering as the next real feature.
