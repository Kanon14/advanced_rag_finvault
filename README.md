# FinVault (Stage 0-2 Complete)

FinVault is a local-first, staged Python project for experimenting with ingestion and retrieval workflows over financial documents.

Current implementation status:

- Stage 0: uv project setup and smoke scaffolding
- Stage 1: mocked FastAPI backend API contract
- Stage 2: Streamlit frontend skeleton wired to mocked backend

## Stage 2 Scope

Stage 2 adds a debug-friendly Streamlit app that exercises the existing mocked backend contract end-to-end.

Implemented in Stage 2:

- app header and clear UI sections
- backend health check UI (`GET /health`)
- ingest submit UI (`POST /ingest`)
- ingest status check UI (`GET /ingest/{job_id}/status`)
- chat UI (`POST /chat`)
- answer and citations rendering
- debug panel with raw request/response payloads
- small frontend service layer (`frontend/services/api_client.py`)
- environment-based backend URL config (`frontend/config.py`)

Still intentionally mocked in Stage 2:

- no real file parsing/Docling
- no Qdrant integration
- no Ollama integration
- no LangGraph orchestration
- no SSE streaming
- no background workers or database layer

## Project Layout

```text
finvault/
  backend/
    main.py
    api/
    core/
    schemas/
    services/
  frontend/
    app.py
    config.py
    components/
      sections.py
    services/
      api_client.py
  data/
  scripts/
  tests/
  .env.example
  pyproject.toml
  README.md
```

## Environment

Copy `.env.example` to `.env` and keep local values:

```powershell
Copy-Item .env.example .env
```

Important variables for Stage 2:

- `BACKEND_HOST=127.0.0.1`
- `BACKEND_PORT=8000`
- `FRONTEND_HOST=127.0.0.1`
- `FRONTEND_PORT=8501`

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

## How to Test Stage 2 UI

Open frontend:

```text
http://127.0.0.1:8501
```

Open backend docs (optional cross-check):

```text
http://127.0.0.1:8000/docs
```

UI sections to test:

1. Backend Health
   - click `Check backend health`
   - expect reachable status payload
2. Ingestion Request
   - choose `source_type=pdf`
   - enter local path in `source_value` (or use optional picker name helper)
   - click `Submit ingest request`
   - expect `job_id` and `queued`
3. Ingestion Status
   - verify `job_id` auto-fills from last ingest
   - click `Check ingestion status`
   - expect mocked status/progress/detail
4. Chat
   - enter a question
   - click `Send chat request`
   - expect mocked answer and citations table
5. Debug Panel
   - verify raw request/response event history appears for each action

## Sample User Flow

1. Start backend and frontend
2. Run health check from UI
3. Submit ingest payload for local PDF path
4. Copy/reuse returned `job_id` in status section
5. Ask a chat question
6. Inspect debug panel for payload correctness

## Manual Verification Checklist

- backend reachable from frontend health section
- ingest call returns mock `job_id`
- status call returns mocked progress for provided `job_id`
- chat call returns mocked `answer` and `citations`
- debug panel shows raw event payloads
- errors are shown clearly when backend is offline or payload is invalid

## Likely Failure Points and Debugging Tips

- Backend offline: health and other calls fail; start backend first
- Wrong host/port in `.env`: confirm `BACKEND_HOST` and `BACKEND_PORT`
- 422 from ingest/chat: check required fields in debug panel payload
- Empty `source_value` for ingest: backend validation rejects request
- Windows command/port conflicts: free port or change launch port values

## Stage 3 Preview

1. Add thin ingestion adapters and stronger payload validation rules
2. Add retrieval/storage interfaces for future local vector integration
3. Add LLM adapter boundary for future local inference integration
4. Expand frontend/backend contract tests around failure scenarios
