"""
Endpoints для системной информации
"""
from fastapi import APIRouter
import platform
import sys
import psutil
import os
from pathlib import Path

from app.core.config import settings

router = APIRouter()


@router.get("/info")
async def get_system_info():
    """Получить информацию о системе"""
    return {
        "system": {
            "os": platform.system(),
            "os_version": platform.version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "python": {
            "version": sys.version,
            "executable": sys.executable,
        },
        "app": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "workstation_id": settings.get_workstation_id()
        },
        "resources": {
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
            "disk_free_gb": round(psutil.disk_usage('/').free / (1024**3), 2),
        }
    }


@router.get("/health/detailed")
async def detailed_health():
    """Детальная проверка здоровья системы"""
    # Проверка директорий
    dirs_status = {}
    for name, path in {
        "watch": settings.WATCH_FOLDER,
        "processed": settings.PROCESSED_FOLDER,
        "database": settings.DATABASE_PATH.parent,
        "cache": settings.CACHE_DIR,
        "logs": settings.LOGS_DIR,
    }.items():
        dirs_status[name] = {
            "exists": path.exists(),
            "path": str(path),
            "writable": path.exists() and os.access(path, os.W_OK)
        }
    
    # Проверка БД
    db_ok = settings.DATABASE_PATH.exists()
    
    return {
        "status": "healthy" if db_ok else "degraded",
        "directories": dirs_status,
        "database": {
            "exists": db_ok,
            "path": str(settings.DATABASE_PATH),
            "size_mb": round(settings.DATABASE_PATH.stat().st_size / (1024**2), 2) if db_ok else 0
        }
    }
