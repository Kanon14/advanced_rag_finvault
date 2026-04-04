from __future__ import annotations

from typing import Any

import httpx


class ApiClient:
    def __init__(self, base_url: str, timeout_seconds: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            response = httpx.request(
                method=method,
                url=url,
                json=payload,
                timeout=self.timeout_seconds,
            )
            try:
                body: Any = response.json()
            except ValueError:
                body = {"raw_text": response.text}

            if response.status_code >= 400:
                return {
                    "ok": False,
                    "url": url,
                    "status_code": response.status_code,
                    "error": "HTTP error from backend",
                    "data": body,
                    "request_payload": payload,
                }

            return {
                "ok": True,
                "url": url,
                "status_code": response.status_code,
                "data": body,
                "request_payload": payload,
            }
        except Exception as exc:
            return {
                "ok": False,
                "url": url,
                "status_code": None,
                "error": str(exc),
                "data": None,
                "request_payload": payload,
            }

    def get_health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def post_ingest(
        self, source_type: str, source_value: str, metadata: dict[str, Any]
    ) -> dict[str, Any]:
        payload = {
            "source_type": source_type,
            "source_value": source_value,
            "metadata": metadata,
        }
        return self._request("POST", "/ingest", payload=payload)

    def get_ingest_status(self, job_id: str) -> dict[str, Any]:
        return self._request("GET", f"/ingest/{job_id}/status")

    def post_chat(self, question: str, session_id: str | None, top_k: int) -> dict[str, Any]:
        payload = {
            "question": question,
            "session_id": session_id,
            "top_k": top_k,
        }
        return self._request("POST", "/chat", payload=payload)
