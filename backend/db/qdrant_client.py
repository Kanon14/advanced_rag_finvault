from __future__ import annotations

from pathlib import Path

from qdrant_client import QdrantClient

from backend.core.config import get_settings

_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is not None:
        return _client

    settings = get_settings()
    if settings.qdrant_mode == "local":
        qdrant_path = Path(settings.qdrant_path)
        qdrant_path.mkdir(parents=True, exist_ok=True)
        _client = QdrantClient(path=str(qdrant_path))
        return _client

    _client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
    )
    return _client
