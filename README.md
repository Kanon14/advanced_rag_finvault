# FinVault (Stage 0-1 Complete)

FinVault is a local-first, staged Python project for experimentation with ingestion and retrieval workflows over financial content.

This repository currently includes:

- Stage 0: project setup and smoke-test scaffolding
- Stage 1: FastAPI backend API contract skeleton with mocked responses

## Current Status (2026-04-04)

Stage 1 backend contract testing is complete in local development.

Validated manually:

- `GET /health` returns service metadata and status
- `POST /ingest` accepts local PDF payload and returns mock `job_id`
- `GET /ingest/{job_id}/status` returns mocked ingestion state
- `POST /chat` returns mocked answer and mocked citations

Current application behavior:

- backend contract is runnable and testable via `/docs`
- ingestion and chat flows are still mocked by design
- no vector database, LLM inference, orchestration, or streaming is connected yet

## Stage 1 Scope

Stage 1 defines the backend API surface needed for future RAG development while keeping all behavior mocked and deterministic.

Implemented in Stage 1:

- `GET /health`
- `POST /ingest`
- `GET /ingest/{job_id}/status`
- `POST /chat`
- Pydantic request/response schemas
- structured JSON logging for debugging
- centralized exception handling for validation and server errors

Intentionally mocked in Stage 1:

- no Docling ingestion
- no Qdrant integration
- no Ollama integration
- no LangGraph orchestration
- no SSE streaming, background jobs, or database layer

## Project Layout

```text
finvault/
  backend/
    __init__.py
    main.py
    api/
      __init__.py
      error_handlers.py
      routes/
        __init__.py
        chat.py
        health.py
        ingest.py
    core/
      __init__.py
      config.py
      logging.py
    schemas/
      __init__.py
      chat.py
      common.py
      ingest.py
    services/
      __init__.py
      mock_chat.py
      mock_ingestion.py
  frontend/
    __init__.py
    app.py
  ingestion/
    __init__.py
  retrieval/
    __init__.py
  llm/
    __init__.py
  db/
    __init__.py
  graph/
    __init__.py
  schemas/
    __init__.py
  tests/
    __init__.py
  scripts/
    smoke_fastapi.py
    smoke_ollama.py
    smoke_qdrant.py
    smoke_streamlit.py
  docs/
    README.md
  .env.example
  .gitignore
  pyproject.toml
  README.md
```

## Initialize with uv (Windows-first)

1) Install uv (if needed):

```powershell
winget install --id=astral-sh.uv -e
```

2) Ensure Python is available via uv:

```powershell
uv python install 3.11
```

3) Create environment and sync dependencies:

```powershell
uv venv
uv sync --dev
```

4) Create local env file:

```powershell
Copy-Item .env.example .env
```

## Run Backend (Stage 1)

```powershell
uv run uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

## Test Endpoints Manually

Health:

```powershell
http://127.0.0.1:8000/health
```

```powershell
http://127.0.0.1:8000/docs
```

Ingest queue:

```powershell
curl -X POST http://127.0.0.1:8000/ingest -H "Content-Type: application/json" -d '{"source_type":"pdf","source_value":"C:/data/mock-report.pdf","metadata":{"ticker":"MSFT"}}'
```

Ingest status: (Checked)

```powershell
curl http://127.0.0.1:8000/ingest/job_a1b2c3d4e5f6/status
```

Chat: (Checked)

```powershell
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d '{"question":"Summarize key risks.","session_id":"demo-session","top_k":2}'
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

## Sample Responses

`GET /health`

```json
{
  "status": "ok",
  "service": "finvault-backend",
  "environment": "local",
  "version": "0.1.0-stage1"
}
```

`POST /ingest`

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "queued",
  "message": "Mock ingestion accepted and queued."
}
```

`GET /ingest/{job_id}/status`

```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "status": "processing",
  "progress": 55,
  "detail": "Parsing and chunking documents (mock)."
}
```

`POST /chat`

```json
{
  "answer": "This is a mocked Stage 1 response. Your question was: 'Summarize key risks.'. No retrieval or LLM inference is running yet.",
  "citations": [
    {
      "source_id": "mock_doc_001",
      "title": "Mock Financial Filing",
      "chunk_id": "chunk_01",
      "score": 0.92
    },
    {
      "source_id": "mock_doc_002",
      "title": "Mock Earnings Call",
      "chunk_id": "chunk_07",
      "score": 0.86
    }
  ],
  "mocked": true
}
```

## Frontend (Still Stage 0 Placeholder)

```powershell
uv run streamlit run frontend/app.py --server.address 127.0.0.1 --server.port 8501
```

## Run Smoke Tests

```powershell
uv run python scripts/smoke_qdrant.py
uv run python scripts/smoke_ollama.py
uv run python scripts/smoke_fastapi.py
uv run python scripts/smoke_streamlit.py
```

Optional tooling checks:

```powershell
uv run ruff check .
uv run pytest -q
```

## Health Checklist

- `uv sync --dev` completes without dependency resolution errors
- backend starts and serves `/docs`
- Stage 1 endpoints return valid JSON payloads
- `smoke_fastapi.py` and `smoke_streamlit.py` pass
- `smoke_qdrant.py` reports reachable local Qdrant (or clear actionable error)
- `smoke_ollama.py` reports reachable local Ollama (or clear actionable error)
- FastAPI docs load at `http://127.0.0.1:8000/docs`
- Streamlit page loads at `http://127.0.0.1:8501`

## Common Windows Setup/Debug Issues

- `uv` not recognized: restart terminal after installation; verify with `uv --version`
- Python mismatch: run `uv python list` and re-run `uv python install 3.11`
- Port conflicts: change ports in command flags or `.env`
- JSON parse errors with `curl` on Windows: prefer PowerShell `Invoke-RestMethod` or escape quotes carefully
- Qdrant not running: start local instance before `smoke_qdrant.py`
- Ollama not running: start Ollama app/service before `smoke_ollama.py`
- Firewall blocks localhost services: allow local inbound loopback ports

## Stage 2 Preview

1. Add ingestion adapters and document normalization flow (still local-first)
2. Introduce storage abstractions for future Qdrant integration (without production coupling)
3. Add local LLM adapter interface for future Ollama integration
4. Expand test coverage for endpoint contracts and service boundaries
