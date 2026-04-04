from fastapi import APIRouter

from backend.api.routes.chat import router as chat_router
from backend.api.routes.health import router as health_router
from backend.api.routes.ingest import router as ingest_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(ingest_router)
api_router.include_router(chat_router)
