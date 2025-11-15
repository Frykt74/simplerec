from fastapi import APIRouter
from .endpoints import health, files, ocr, search

api_router = APIRouter()

# Подключение всех endpoints
api_router.include_router(health.router, tags=["health"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
