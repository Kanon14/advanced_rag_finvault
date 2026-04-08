# FinVault (Stage 0-5 Complete)

FinVault is a local-first, staged Python project for experimenting with ingestion, indexing, retrieval, and baseline RAG generation over financial documents.

Current implementation status:

- Stage 0: uv-native setup and smoke scaffolding
- Stage 1: backend API contract skeleton
- Stage 2: Streamlit frontend connected to backend
- Stage 3: real local ingestion pipeline with artifacts
- Stage 4: local vector indexing and retrieval with Qdrant
- Stage 5: baseline RAG answer generation with Qdrant + Ollama

## Stage 5 Scope

Stage 5 replaces the mocked chat behavior with a real baseline RAG flow:

## Stage 5 Completion Notes (2026-04-08)

Validated in local testing:

- end-to-end baseline RAG flow works: ingestion -> indexing -> retrieval -> chat generation
- `POST /chat` now performs real retrieval + Ollama generation (no mocked answer)
- chat supports optional `collection_name` for per-request collection targeting
- citations include traceable metadata (`chunk_id`, `filename`, `page_number`, `chunk_index`, `snippet`, `document_id`, `ingestion_job_id`)
- frontend chat timeout issue resolved with:
  - `FRONTEND_API_TIMEOUT_SECONDS=30`
  - `FRONTEND_CHAT_TIMEOUT_SECONDS=120`
- chat debug artifacts are generated under `data/chat/<request_id>/`

1. embed query using Stage 4 embedding boundary
2. retrieve top-k chunks from Qdrant
3. build deterministic context + prompt
4. call Ollama for generation
5. return answer + traceable citations

Implemented in Stage 5:

- real `POST /chat` retrieval + generation pipeline
- Ollama generation adapter boundary (`backend/llm/ollama_client.py`)
- context/prompt builder service (`backend/services/context_builder.py`)
- chat debug artifacts under `data/chat/<request_id>/`
- additive chat response fields: `request_id`, `model`, `retrieval_count`

Still intentionally not implemented:

- LangGraph orchestration
- SSE streaming
- reranking
- HyDE
- hybrid retrieval

## Chat API Contract (Stage 5)

Request remains stable:

```json
{
  "question": "Summarize major risk factors",
  "session_id": "demo-session",
  "top_k": 3,
  "collection_name": "finvault_chunks"
}
```

`collection_name` is optional. If omitted, backend uses `QDRANT_COLLECTION` from environment.

Response now returns real generation output and additive debug fields:

```json
{
  "answer": "...",
  "citations": [
    {
      "source_id": "...",
      "title": "...",
      "chunk_id": "...",
      "score": 0.82,
      "filename": "...",
      "page_number": 2,
      "chunk_index": 5,
      "snippet": "...",
      "document_id": "...",
      "ingestion_job_id": "..."
    }
  ],
  "mocked": false,
  "request_id": "chat_xxxxx",
  "model": "llama3.2",
  "retrieval_count": 3
}
```

## Environment Configuration

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Key Stage 4/5 fields:

- `FRONTEND_API_TIMEOUT_SECONDS=30`
- `FRONTEND_CHAT_TIMEOUT_SECONDS=120`
- `QDRANT_MODE=local`
- `QDRANT_PATH=data/qdrant`
- `QDRANT_COLLECTION=finvault_chunks`
- `EMBEDDING_PROVIDER=hash`
- `EMBEDDING_DIMENSION=256`
- `OLLAMA_BASE_URL=http://127.0.0.1:11434`
- `OLLAMA_MODEL=llama3.2`
- `OLLAMA_TIMEOUT_SECONDS=90`

## Run with uv

Install/sync dependencies:

```powershell
uv venv
uv sync --dev
```

Run backend:

```powershell
uv run uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Run frontend:

```powershell
uv run streamlit run frontend/app.py --server.address 127.0.0.1 --server.port 8501
```

Start Ollama and ensure model exists:

```powershell
ollama serve
ollama pull llama3.2
```

## Full Baseline RAG Flow Test

1. Ingest a PDF (path or upload endpoint)
2. Wait for ingestion status `completed`
3. Index artifacts via `POST /index/{job_id}`
4. Query retrieval via `POST /retrieve` (optional check)
5. Call `POST /chat` for generated answer

Example calls:

```powershell
curl -X POST "http://127.0.0.1:8000/ingest/upload" -F "file=@C:/Users/you/Documents/report.pdf" -F "metadata_json={\"ticker\":\"MSFT\"}"
curl -X POST "http://127.0.0.1:8000/index/<job_id>" -H "Content-Type: application/json" -d "{}"
curl -X POST "http://127.0.0.1:8000/chat" -H "Content-Type: application/json" -d "{\"question\":\"Summarize key risks\",\"top_k\":3,\"collection_name\":\"finvault_chunks\"}"
```

## Debug Artifacts and Logs

Ingestion artifacts:

- `data/ingestion/<job_id>/...`

Indexing debug output:

- `data/indexing/<job_id>/index_summary.json`

Chat debug output:

- `data/chat/<request_id>/question.txt`
- `data/chat/<request_id>/retrieval.json`
- `data/chat/<request_id>/prompt.txt`
- `data/chat/<request_id>/llm_response.json` (if generation succeeds)

## Manual Verification Checklist

- ingestion still completes and writes artifacts
- indexing returns non-zero indexed chunks
- retrieval returns matches and metadata
- `/chat` returns non-mocked answer and citations when Ollama is available
- fallback response is returned when retrieval context is unavailable
- `/chat` returns actionable 503 when Ollama is unavailable but retrieval context exists

## Common Stage 5 Issues

- Ollama not running: start with `ollama serve`
- model missing: run `ollama pull <model>`
- no retrieval matches: verify indexing completed in same collection
- collection not found: run indexing before chat/retrieve
- weak answer quality: expected with baseline hash embeddings and simple prompting

## Stage 6 Preview

1. improve embedding quality with replaceable provider upgrades
2. add retrieval quality controls and filtering heuristics
3. prepare orchestration boundaries for future graph-based flows
4. improve prompt/citation diagnostics for iterative tuning
