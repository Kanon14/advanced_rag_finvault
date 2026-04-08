from dataclasses import dataclass
from functools import lru_cache
import os

from dotenv import load_dotenv


def _as_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = "FinVault Backend"
    app_version: str = "0.1.0-stage5"
    app_env: str = "local"
    app_debug: bool = True
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    qdrant_mode: str = "local"
    qdrant_path: str = "data/qdrant"
    qdrant_url: str = "http://127.0.0.1:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "finvault_chunks"
    embedding_provider: str = "hash"
    embedding_dimension: int = 256
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout_seconds: int = 90


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        app_env=os.getenv("APP_ENV", "local"),
        app_debug=_as_bool(os.getenv("APP_DEBUG", "true"), default=True),
        backend_host=os.getenv("BACKEND_HOST", "127.0.0.1"),
        backend_port=int(os.getenv("BACKEND_PORT", "8000")),
        qdrant_mode=os.getenv("QDRANT_MODE", "local"),
        qdrant_path=os.getenv("QDRANT_PATH", "data/qdrant"),
        qdrant_url=os.getenv("QDRANT_URL", "http://127.0.0.1:6333"),
        qdrant_api_key=os.getenv("QDRANT_API_KEY", ""),
        qdrant_collection=os.getenv("QDRANT_COLLECTION", "finvault_chunks"),
        embedding_provider=os.getenv("EMBEDDING_PROVIDER", "hash"),
        embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "256")),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        ollama_timeout_seconds=int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "90")),
    )
