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
        existing_size = get_collection_vector_size(client, collection_name)
        if existing_size is not None and existing_size != vector_size:
            raise ValueError(
                "Qdrant collection dimension mismatch for "
                f"'{collection_name}': existing={existing_size}, requested={vector_size}. "
                "Use a matching EMBEDDING_DIMENSION or a new collection name."
            )
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


def get_collection_vector_size(client: QdrantClient, collection_name: str) -> int | None:
    info = client.get_collection(collection_name=collection_name)
    vectors = info.config.params.vectors

    if hasattr(vectors, "size"):
        return int(vectors.size)
    if isinstance(vectors, dict) and vectors:
        first = next(iter(vectors.values()))
        if hasattr(first, "size"):
            return int(first.size)
    return None
