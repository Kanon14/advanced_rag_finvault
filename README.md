# FinVault (Stage 0-4 Complete)

FinVault is a local-first, staged Python project for experimenting with ingestion and retrieval workflows over financial documents.

Current implementation status:

- Stage 0: uv-native setup and smoke scaffolding
- Stage 1: mocked FastAPI backend contract
- Stage 2: Streamlit frontend connected to backend
- Stage 3: real local ingestion pipeline with debug artifacts
- Stage 4: local vector indexing and retrieval with Qdrant

## Stage 4 Scope

Stage 4 adds vector indexing and retrieval on top of Stage 3 artifacts.

## Stage 4 Completion Notes (2026-04-06)

Validated in local testing:

- Stage 3 ingestion -> `POST /index/{job_id}` flow works end-to-end
- local Qdrant storage is created under `data/qdrant/`
- indexing summary is generated at `data/indexing/<job_id>/index_summary.json`
- `POST /retrieve` returns matched chunks with scores
- retrieval results include traceable metadata for citation inspection

Implemented in Stage 4:

- local-first Qdrant storage boundary
- embedding adapter boundary with default deterministic hash embedder
- indexing endpoint to read `data/ingestion/<job_id>/chunks.json` and upsert vectors
- retrieval endpoint for query-time vector search (no answer generation)
- structured logging for collection setup, indexing, and retrieval
- indexing debug summaries under `data/indexing/<job_id>/index_summary.json`

Still intentionally not implemented:

- answer generation from LLM
- Ollama integration
- LangGraph orchestration
- SSE streaming
- reranking / HyDE / hybrid retrieval

## New API Endpoints

- `POST /index/{job_id}`: index one completed ingestion job into Qdrant
- `POST /retrieve`: vector search test endpoint returning matched chunks/scores/metadata

Existing ingestion and chat endpoints remain available.

## Qdrant Local Mode

Default mode is local and file-backed:

- `QDRANT_MODE=local`
- `QDRANT_PATH=data/qdrant`

This avoids external infra for local development.

Switch to hosted later by setting:

- `QDRANT_MODE=remote`
- `QDRANT_URL=...`
- `QDRANT_API_KEY=...`

## Embedding Configuration

Default embedder:

- `EMBEDDING_PROVIDER=hash`
- `EMBEDDING_DIMENSION=256`

Embedding dimension is configured in `.env` and must match collection vector size.

## Run with uv

Install/sync dependencies:

```powershell
uv venv
uv sync --dev
```

Run backend (Terminal 1):

```powershell
uv run uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Run frontend (Terminal 2):

```powershell
uv run streamlit run frontend/app.py --server.address 127.0.0.1 --server.port 8501
```

## How to Index Stage 3 Artifacts

1. Run ingestion (Stage 3) and get `job_id`
2. Index it:

```powershell
curl -X POST "http://127.0.0.1:8000/index/<job_id>" -H "Content-Type: application/json" -d "{}"
```

Optional custom collection:

```powershell
curl -X POST "http://127.0.0.1:8000/index/<job_id>" -H "Content-Type: application/json" -d "{\"collection_name\":\"finvault_chunks\"}"
```

Index response includes:

- `job_id`
- `document_id`
- `collection_name`
- `chunk_count`
- `indexed_count`
- `embedding_provider`
- `embedding_dimension`
- `status`
- `errors`

## How to Test Retrieval

```powershell
curl -X POST "http://127.0.0.1:8000/retrieve" -H "Content-Type: application/json" -d "{\"query\":\"key risk factors and summary\",\"top_k\":5}"
```

Response returns:

- `matches[]` with `score`
- `chunk_id`
- `text`
- traceable metadata (`document_id`, `source_id`, `filename`, `page_number`, `chunk_index`, `snippet`, `ingestion_job_id`)

## Debug Artifacts

- ingestion artifacts: `data/ingestion/<job_id>/...`
- indexing summary: `data/indexing/<job_id>/index_summary.json`
- local qdrant files: `data/qdrant/`

## Manual Verification Checklist

- Stage 3 ingestion still succeeds and writes chunk artifacts
- `POST /index/{job_id}` returns summary with non-zero `indexed_count`
- `data/qdrant/` exists in local mode
- `data/indexing/<job_id>/index_summary.json` is created
- `POST /retrieve` returns matches with score + traceable metadata
- existing `/chat` endpoint still behaves as before (mocked)

## Common Stage 4 Issues

- `Missing chunks artifact`: run Stage 3 ingestion first
- empty retrieval matches: ensure indexing ran on correct collection
- vector size mismatch: check `EMBEDDING_DIMENSION`
- local qdrant lock/path issues: stop conflicting process, verify `QDRANT_PATH`
- low retrieval quality: expected with deterministic hash embedding (upgrade in later stage)

## Stage 5 Preview

1. Add better embedding providers (adapter remains replaceable)
2. Tie retrieval results into chat context assembly
3. Prepare generation boundary (still modular)
4. Expand retrieval evaluation/debug tooling
