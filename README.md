# FinVault (Stage 0-6 Complete)

FinVault is a local-first, staged Python project for ingestion, indexing, retrieval, and baseline RAG generation over financial documents.

Current implementation status:

- Stage 0: uv-native setup and smoke scaffolding
- Stage 1: backend API contract skeleton
- Stage 2: Streamlit frontend connected to backend
- Stage 3: real ingestion pipeline with local artifacts
- Stage 4: local Qdrant indexing and retrieval
- Stage 5: baseline RAG answer generation with Qdrant + Ollama
- Stage 6: retrieval quality controls, embedding upgrades, and diagnostics hardening

## Stage 6 Scope

Stage 6 improves retrieval quality and debuggability without adding orchestration complexity.

## Stage 6 Completion Notes (2026-04-10)

Validated in local testing:

- ingestion -> indexing -> retrieval -> chat flow works end-to-end
- retrieval diagnostics are generated with raw/included/excluded counts and reasons
- chat diagnostics are generated and persisted in `data/chat/<request_id>/diagnostics.json`
- collection-specific testing works via additive `collection_name` request field
- frontend chat timeout behavior is stabilized for local Ollama runs

Repository cleanup completed (conservative):

- removed unused mock service files from `backend/services/`
- removed unused root-level placeholder package stubs (`ingestion/`, `retrieval/`, `llm/`, `db/`, `graph/`, `schemas/`)
- updated frontend header text to match current Stage 6 runtime
- lint and tests pass after cleanup

Implemented in Stage 6:

- embedding provider upgrades behind existing adapter boundary
- provider selection by environment (`hash` or `ollama`)
- retrieval filtering controls:
  - score threshold
  - max context character budget
  - deduplication of near-identical chunks
  - optional unique page control
- richer retrieval/chat diagnostics:
  - raw candidate count
  - filtered candidate count
  - exclusion reasons summary
  - context size summary
- richer citation diagnostics fields:
  - `retrieval_rank`
  - `included_in_prompt`
  - `filtered_out_reason`
- chat debug artifacts now include `diagnostics.json`

Still intentionally not implemented:

- LangGraph orchestration
- SSE streaming
- reranking
- HyDE
- hybrid retrieval

## Embedding Providers

Supported providers:

- `hash` (fast baseline; lower semantic quality)
- `ollama` (local model embeddings; higher quality potential)

Configuration:

- `EMBEDDING_PROVIDER=hash|ollama`
- `EMBEDDING_MODEL=nomic-embed-text` (used for `ollama` provider)
- `EMBEDDING_DIMENSION=<int>`

Dimension rules:

- Hash provider uses `EMBEDDING_DIMENSION` directly.
- Ollama provider must match model output dimension.
- If collection dimension mismatches configured dimension, indexing returns a clear actionable error.

## Retrieval Quality Controls

Controls are available via environment defaults and per-request overrides on `/retrieve` and `/chat`.

Environment defaults:

- `RETRIEVAL_MIN_SCORE`
- `RETRIEVAL_MAX_CONTEXT_CHARS`
- `RETRIEVAL_DEDUPLICATE`
- `RETRIEVAL_UNIQUE_PAGES`

Per-request additive fields:

- `min_score`
- `max_context_chars`
- `deduplicate`
- `unique_pages`

## Chat API (Stage 6)

Request shape remains stable and additive:

```json
{
  "question": "Summarize major risk factors",
  "session_id": "demo-session",
  "top_k": 5,
  "collection_name": "finvault_chunks",
  "min_score": 0.0,
  "max_context_chars": 5000,
  "deduplicate": true,
  "unique_pages": false
}
```

Response includes answer, citations, and diagnostics:

```json
{
  "answer": "...",
  "citations": [
    {
      "chunk_id": "...",
      "score": 0.21,
      "filename": "...",
      "page_number": 10,
      "chunk_index": 52,
      "snippet": "...",
      "document_id": "...",
      "ingestion_job_id": "...",
      "retrieval_rank": 1,
      "included_in_prompt": true,
      "filtered_out_reason": null
    }
  ],
  "mocked": false,
  "request_id": "chat_xxxxx",
  "model": "llama3.2",
  "retrieval_count": 5,
  "diagnostics": {
    "provider": "hash",
    "embedding_dimension": 256,
    "raw_candidate_count": 20,
    "included_count": 5,
    "excluded_count": 7,
    "excluded_reasons": {
      "below_score_threshold": 4,
      "duplicate_text": 3
    },
    "context_chars": 4872
  }
}
```

## Environment Configuration

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Key fields:

- `FRONTEND_API_TIMEOUT_SECONDS=30`
- `FRONTEND_CHAT_TIMEOUT_SECONDS=120`
- `QDRANT_MODE=local`
- `QDRANT_PATH=data/qdrant`
- `QDRANT_COLLECTION=finvault_chunks`
- `EMBEDDING_PROVIDER=hash`
- `EMBEDDING_MODEL=nomic-embed-text`
- `EMBEDDING_DIMENSION=256`
- `RETRIEVAL_MIN_SCORE=-1.0`
- `RETRIEVAL_MAX_CONTEXT_CHARS=6000`
- `RETRIEVAL_DEDUPLICATE=true`
- `RETRIEVAL_UNIQUE_PAGES=false`
- `OLLAMA_BASE_URL=http://127.0.0.1:11434`
- `OLLAMA_MODEL=llama3.2`
- `OLLAMA_TIMEOUT_SECONDS=90`

## Run with uv

```powershell
uv venv
uv sync --dev
uv run uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
uv run streamlit run frontend/app.py --server.address 127.0.0.1 --server.port 8501
```

Ollama setup (if using ollama embedding provider or chat generation):

```powershell
ollama serve
ollama pull llama3.2
ollama pull nomic-embed-text
```

## Baseline Flow Test

1. Ingest PDF (`/ingest` or `/ingest/upload`)
2. Wait for ingestion status `completed`
3. Index job via `POST /index/{job_id}`
4. Inspect retrieval via `POST /retrieve`
5. Run `POST /chat` and inspect citations/diagnostics

Example calls:

```powershell
curl -X POST "http://127.0.0.1:8000/index/<job_id>" -H "Content-Type: application/json" -d "{}"
curl -X POST "http://127.0.0.1:8000/retrieve" -H "Content-Type: application/json" -d "{\"query\":\"key risks\",\"top_k\":8,\"min_score\":0.0,\"max_context_chars\":4000,\"deduplicate\":true}"
curl -X POST "http://127.0.0.1:8000/chat" -H "Content-Type: application/json" -d "{\"question\":\"Summarize key risks\",\"top_k\":6,\"collection_name\":\"finvault_chunks\",\"min_score\":0.0,\"max_context_chars\":4000}"
```

## Diagnostics and Debug Artifacts

- ingestion artifacts: `data/ingestion/<job_id>/...`
- indexing summary: `data/indexing/<job_id>/index_summary.json`
- chat artifacts:
  - `data/chat/<request_id>/question.txt`
  - `data/chat/<request_id>/retrieval.json`
  - `data/chat/<request_id>/prompt.txt`
  - `data/chat/<request_id>/diagnostics.json`
  - `data/chat/<request_id>/llm_response.json` (when generation succeeds)

## Common Stage 6 Issues

- embedding provider misconfigured (`hash|ollama` only)
- embedding dimension mismatch with existing collection
- score threshold too high causing no context
- context budget too small for useful grounding
- Ollama service/model unavailable

## Stage 7 Preview

1. introduce orchestration-ready execution boundaries
2. add richer retrieval evaluation and quality reporting
3. improve answer grounding diagnostics and prompt iteration tools
4. keep architecture compatible for future graph orchestration stage
