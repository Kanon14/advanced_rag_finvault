from fastapi import APIRouter

from backend.core.config import get_settings
from backend.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service="finvault-backend",
        environment=settings.app_env,
        version=settings.app_version,
    )
