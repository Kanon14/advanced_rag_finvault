# FinVault (Stage 0 Scaffold)

FinVault is a local-first, staged Python project for experimenting with document ingestion and retrieval workflows over financial content.

This repository is currently **Stage 0** only: project setup, environment scaffolding, and smoke-test checks.

## Current Scope (Implemented)

- uv-native project setup with `pyproject.toml` as source of truth
- Minimal backend placeholder using FastAPI
- Minimal frontend placeholder using Streamlit
- Smoke-test scripts for Qdrant, Ollama, FastAPI, and Streamlit
- Stage-ready module layout for future expansion

## Intentionally Not Implemented Yet

- No LangGraph orchestration
- No Docling ingestion pipeline
- No RAG logic (chunking, embeddings, retrieval, reranking, HyDE)
- No hybrid search, SSE streaming, or advanced observability stack
- No business/domain logic beyond setup smoke checks

## Project Layout

```text
finvault/
  backend/
    __init__.py
    main.py
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

## Run Apps

Backend (FastAPI):

```powershell
uv run uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend (Streamlit):

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
- `smoke_fastapi.py` and `smoke_streamlit.py` pass
- `smoke_qdrant.py` reports reachable local Qdrant (or clear actionable error)
- `smoke_ollama.py` reports reachable local Ollama (or clear actionable error)
- FastAPI docs load at `http://127.0.0.1:8000/docs`
- Streamlit page loads at `http://127.0.0.1:8501`

## Common Windows Setup/Debug Issues

- `uv` not recognized: restart terminal after installation; verify with `uv --version`
- Python mismatch: run `uv python list` and re-run `uv python install 3.11`
- Port conflicts: change ports in command flags or `.env`
- Qdrant not running: start local instance before `smoke_qdrant.py`
- Ollama not running: start Ollama app/service before `smoke_ollama.py`
- Firewall blocks localhost services: allow local inbound loopback ports

## Next Stages

1. Add Docling-powered ingestion skeleton and markdown persistence
2. Add db/retrieval abstractions with basic vector indexing and query interfaces
3. Add llm provider wrapper for Ollama with prompt/response schemas
4. Introduce graph orchestration module (LangGraph) once core modules are stable
