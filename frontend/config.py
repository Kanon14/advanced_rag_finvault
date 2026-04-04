from dataclasses import dataclass
from functools import lru_cache
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class FrontendSettings:
    app_env: str
    app_debug: bool
    backend_host: str
    backend_port: int
    frontend_host: str
    frontend_port: int

    @property
    def backend_base_url(self) -> str:
        return f"http://{self.backend_host}:{self.backend_port}"


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def get_settings() -> FrontendSettings:
    load_dotenv()
    return FrontendSettings(
        app_env=os.getenv("APP_ENV", "local"),
        app_debug=_to_bool(os.getenv("APP_DEBUG", "true"), default=True),
        backend_host=os.getenv("BACKEND_HOST", "127.0.0.1"),
        backend_port=int(os.getenv("BACKEND_PORT", "8000")),
        frontend_host=os.getenv("FRONTEND_HOST", "127.0.0.1"),
        frontend_port=int(os.getenv("FRONTEND_PORT", "8501")),
    )
