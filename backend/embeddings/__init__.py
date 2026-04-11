from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.embeddings.base import Embedder
from backend.embeddings.hash_embedder import HashEmbedder
from backend.embeddings.ollama_embedder import OllamaEmbedder

logger = get_logger(__name__)


def build_embedder(dimension: int | None = None) -> Embedder:
    settings = get_settings()
    raw_provider = settings.embedding_provider.strip()
    provider = raw_provider.lower()
    dim = dimension if dimension is not None else settings.embedding_dimension
    embedding_model = settings.embedding_model

    if provider not in {"hash", "ollama"}:
        provider = "ollama"
        embedding_model = raw_provider
        logger.warning(
            "EMBEDDING_PROVIDER='%s' is not a provider name. "
            "Treating it as EMBEDDING_MODEL and using provider='ollama'.",
            raw_provider,
        )

    if provider == "hash":
        return HashEmbedder(dimension=dim)

    if provider == "ollama":
        return OllamaEmbedder(
            base_url=settings.ollama_base_url,
            model=embedding_model,
            timeout_seconds=settings.ollama_timeout_seconds,
            expected_dimension=dim if dim > 0 else None,
        )

    raise ValueError(
        f"Unsupported embedding provider '{settings.embedding_provider}'. Supported: hash, ollama."
    )
