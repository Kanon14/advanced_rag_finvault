from __future__ import annotations

import json
from typing import Any

import httpx


class ApiClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 30.0,
        chat_timeout_seconds: float | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.chat_timeout_seconds = chat_timeout_seconds or timeout_seconds

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

    def post_ingest_upload(
        self, filename: str, file_bytes: bytes, metadata: dict[str, Any]
    ) -> dict[str, Any]:
        url = f"{self.base_url}/ingest/upload"
        try:
            response = httpx.post(
                url,
                data={"metadata_json": json.dumps(metadata)},
                files={"file": (filename, file_bytes, "application/pdf")},
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
                    "request_payload": {"filename": filename, "metadata": metadata},
                }

            return {
                "ok": True,
                "url": url,
                "status_code": response.status_code,
                "data": body,
                "request_payload": {"filename": filename, "metadata": metadata},
            }
        except Exception as exc:
            return {
                "ok": False,
                "url": url,
                "status_code": None,
                "error": str(exc),
                "data": None,
                "request_payload": {"filename": filename, "metadata": metadata},
            }

    def get_ingest_status(self, job_id: str) -> dict[str, Any]:
        return self._request("GET", f"/ingest/{job_id}/status")

    def post_chat(
        self,
        question: str,
        session_id: str | None,
        top_k: int,
        collection_name: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "question": question,
            "session_id": session_id,
            "top_k": top_k,
            "collection_name": collection_name,
        }
        url = f"{self.base_url}/chat"
        try:
            response = httpx.post(url, json=payload, timeout=self.chat_timeout_seconds)
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
                "error": f"{exc}. Consider increasing FRONTEND_CHAT_TIMEOUT_SECONDS.",
                "data": None,
                "request_payload": payload,
            }
