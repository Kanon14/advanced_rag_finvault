from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from backend.core.logging import get_logger

logger = get_logger(__name__)


def _collection_exists(client: QdrantClient, collection_name: str) -> bool:
    try:
        return client.collection_exists(collection_name=collection_name)
    except Exception:
        collections = client.get_collections().collections
        return any(item.name == collection_name for item in collections)


def ensure_collection(client: QdrantClient, collection_name: str, vector_size: int) -> None:
    if _collection_exists(client, collection_name):
        logger.info("Qdrant collection already exists: %s", collection_name)
        return

    logger.info(
        "Creating Qdrant collection name=%s vector_size=%s distance=cosine",
        collection_name,
        vector_size,
    )
    client.create_collection(
        collection_name=collection_name,
        vectors_config=qmodels.VectorParams(
            size=vector_size,
            distance=qmodels.Distance.COSINE,
        ),
    )
