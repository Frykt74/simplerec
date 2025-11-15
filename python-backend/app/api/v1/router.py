from fastapi import APIRouter
from .endpoints import (
    health, files, ocr, search, documents,
    settings, stats, upload, bulk, export, system,
    maintenance
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(stats.router, prefix="/stats", tags=["statistics"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(bulk.router, prefix="/bulk", tags=["bulk"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
