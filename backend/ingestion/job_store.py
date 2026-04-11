from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from threading import Lock
from typing import Any

from backend.ingestion.artifacts import ensure_job_dir, write_json
from backend.ingestion.models import IngestionStatus, JobState


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, JobState] = {}
        self._lock = Lock()

    def create(self, job_id: str, source_type: str, source_value: str) -> JobState:
        state = JobState(
            job_id=job_id,
            status="queued",
            progress=5,
            detail="Ingestion job queued.",
            source_type=source_type,
            source_value=source_value,
            summary={"created_at": self._now_iso()},
        )
        with self._lock:
            self._jobs[job_id] = state
        self._persist_state(state)
        return state

    def update(
        self,
        job_id: str,
        *,
        status: IngestionStatus,
        progress: int,
        detail: str,
        artifacts: dict[str, str] | None = None,
        summary: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> JobState:
        with self._lock:
            state = self._jobs[job_id]
            state.status = status
            state.progress = progress
            state.detail = detail
            if artifacts is not None:
                state.artifacts = artifacts
            if summary is not None:
                state.summary = summary
            state.error = error
        self._persist_state(state)
        return state

    def get(self, job_id: str) -> JobState | None:
        with self._lock:
            return self._jobs.get(job_id)

    def _persist_state(self, state: JobState) -> None:
        payload = asdict(state)
        payload["updated_at"] = self._now_iso()
        status_path = ensure_job_dir(state.job_id) / "status.json"
        write_json(status_path, payload)

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
