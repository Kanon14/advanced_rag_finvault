from fastapi import FastAPI

from backend.api.error_handlers import register_exception_handlers
from backend.api.routes import api_router
from backend.core.config import get_settings
from backend.core.logging import configure_logging, get_logger

settings = get_settings()
configure_logging(debug=settings.app_debug)
logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)
app.include_router(api_router)
register_exception_handlers(app)

logger.info("FastAPI app initialized")
