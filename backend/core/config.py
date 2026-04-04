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
    app_version: str = "0.1.0-stage1"
    app_env: str = "local"
    app_debug: bool = True
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        app_env=os.getenv("APP_ENV", "local"),
        app_debug=_as_bool(os.getenv("APP_DEBUG", "true"), default=True),
        backend_host=os.getenv("BACKEND_HOST", "127.0.0.1"),
        backend_port=int(os.getenv("BACKEND_PORT", "8000")),
    )
