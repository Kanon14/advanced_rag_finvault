# FinVault (Stage 0-3 Complete)

FinVault is a local-first, staged Python project for experimenting with document ingestion and retrieval workflows over financial documents.

Current implementation status:

- Stage 0: uv-native setup and smoke scaffolding
- Stage 1: mocked FastAPI backend contract
- Stage 2: Streamlit frontend connected to backend
- Stage 3: real local ingestion pipeline with debug artifacts

## Stage 3 Completion Notes (2026-04-04)

Validated in local testing:

- Streamlit health check works against local FastAPI backend
- path-based ingestion works with valid PDF paths
- upload-based ingestion works from any local file location via `Upload selected PDF and ingest`
- status polling reflects realistic stage transitions through completion
- chat flow remains functional with existing mocked chat contract
- ingestion artifacts are generated under `data/ingestion/<job_id>/`

## Stage 3 Scope

Stage 3 replaces mocked ingestion with a real local pipeline for PDF input.

Implemented in Stage 3:

- real ingestion jobs created by `POST /ingest`
- realistic stage progress via `GET /ingest/{job_id}/status`
- local file validation and clear error messages
- parser adapter boundary (Docling-ready) with `pypdf` runtime parser
- deterministic normalization and chunking
- artifact output under `data/ingestion/<job_id>/`
- traceable chunk metadata for future citations

Still intentionally not implemented:

- Qdrant/vector storage integration
- embeddings and retrieval pipeline
- Ollama integration
- LangGraph orchestration
- SSE streaming
- reranking/hybrid retrieval
- background queue infrastructure

## Backend Ingestion Contract

Existing endpoints remain stable:

- `POST /ingest`
- `POST /ingest/upload`
- `GET /ingest/{job_id}/status`

Status values are now more realistic:

- `queued`
- `validating`
- `parsing`
- `normalizing`
- `chunking`
- `completed`
- `failed`

`POST /ingest` request format (unchanged):

```json
{
  "source_type": "pdf",
  "source_value": "C:/Users/you/path/to/file.pdf",
  "metadata": {
    "ticker": "MSFT"
  }
}
```

`GET /ingest/{job_id}/status` now also returns optional debug fields:

- `artifacts`
- `summary`
- `error`

These are additive fields and remain compatible with the Stage 2 frontend.

## Project Layout (Stage 3 highlights)

```text
backend/
  api/routes/ingest.py
  ingestion/
    validator.py
    parsers/
      base.py
      pypdf_parser.py
      docling_parser.py
    normalizer.py
    chunker.py
    artifacts.py
    job_store.py
  services/
    ingestion_service.py
data/
  ingestion/
frontend/
  app.py
```

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

## Real Ingestion Flow (Stage 3)

1. Submit ingestion request from Streamlit or `/docs`
2. Receive `job_id`
3. Poll `GET /ingest/{job_id}/status`
4. Observe stage progression to `completed`
5. Inspect artifacts in `data/ingestion/<job_id>/`

Upload flow (any local file location, no manual path typing):

1. Open Streamlit UI at `http://127.0.0.1:8501`
2. In Ingestion Request, pick a PDF in the uploader
3. Click `Upload selected PDF and ingest`
4. Use returned `job_id` to check status

Upload API example:

```powershell
curl -X POST "http://127.0.0.1:8000/ingest/upload" -F "file=@C:/Users/you/Documents/report.pdf" -F "metadata_json={\"ticker\":\"MSFT\"}"
```

## Artifact Output

For each completed job:

- `data/ingestion/<job_id>/status.json`
- `data/ingestion/<job_id>/raw_pages.json`
- `data/ingestion/<job_id>/normalized.md`
- `data/ingestion/<job_id>/chunks.json`
- `data/ingestion/<job_id>/metadata.json`
- `data/ingestion/<job_id>/manifest.json`

Chunk records include traceability metadata such as:

- `document_id`
- `source_id`
- `filename`
- `page_number`
- `section`
- `chunk_id`
- `chunk_index`
- `snippet`

## Manual Verification Checklist

- backend starts successfully
- `POST /ingest` with valid PDF path returns `job_id`
- status endpoint transitions through ingestion stages
- completed status includes `artifacts` and `summary`
- artifact files exist on disk under `data/ingestion/<job_id>/`
- Stage 2 Streamlit ingestion/status UI still works without redesign

## Common Parsing/Chunking/Debug Issues

- Invalid path: returns `400` with clear message
- Non-PDF source: rejected by validation
- Empty text extracted from scanned PDF: check `raw_pages.json` and parser output
- Parser errors: check backend logs and `status.json` error field
- Long documents: status may stay in middle stages while processing

## Stage 4 Preview

1. Add local vector storage boundary (still no production infra)
2. Add embedding adapter interfaces and document indexing flow
3. Add retrieval API scaffolding using stored chunks
4. Keep frontend contract stable while enabling first real retrieval path
