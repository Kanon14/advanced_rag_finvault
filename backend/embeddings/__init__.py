from backend.embeddings.base import Embedder
from backend.embeddings.hash_embedder import HashEmbedder


def build_embedder(dimension: int) -> Embedder:
    return HashEmbedder(dimension=dimension)
