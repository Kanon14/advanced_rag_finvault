from fastapi import APIRouter

from backend.api.routes.chat import router as chat_router
from backend.api.routes.health import router as health_router
from backend.api.routes.ingest import router as ingest_router
from backend.api.routes.indexing import router as indexing_router
from backend.api.routes.retrieve import router as retrieve_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(ingest_router)
api_router.include_router(indexing_router)
api_router.include_router(retrieve_router)
api_router.include_router(chat_router)
