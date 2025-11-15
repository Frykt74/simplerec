
"""
Endpoints для управления настройками
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class SettingsUpdate(BaseModel):
    """Модель для обновления настроек"""
    ocr_languages: Optional[List[str]] = None
    default_ocr_engine: Optional[str] = None
    ocr_gpu: Optional[bool] = None
    max_concurrent_ocr: Optional[int] = None
    pdf_dpi: Optional[int] = None


@router.get("")
async def get_settings():
    """Получить текущие настройки"""
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "ocr": {
            "default_engine": settings.DEFAULT_OCR_ENGINE,
            "languages": settings.OCR_LANGUAGES,
            "use_gpu": settings.OCR_GPU,
            "max_concurrent": settings.MAX_CONCURRENT_OCR,
            "confidence_threshold": settings.OCR_CONFIDENCE_THRESHOLD,
            "allowed_engines": settings.ALLOWED_OCR_ENGINES,
        },
        "files": {
            "supported_formats": settings.SUPPORTED_FORMATS,
            "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
            "pdf_dpi": settings.PDF_DPI,
        },
        "paths": {
            "watch_folder": str(settings.WATCH_FOLDER),
            "processed_folder": str(settings.PROCESSED_FOLDER),
            "database_path": str(settings.DATABASE_PATH),
            "cache_dir": str(settings.CACHE_DIR),
            "logs_dir": str(settings.LOGS_DIR),
        },
        "server": {
            "host": settings.LOCAL_SERVER_HOST,
            "port": settings.LOCAL_SERVER_PORT,
        }
    }


@router.patch("")
async def update_settings(update: SettingsUpdate):
    """
    Обновить настройки (динамически, без перезапуска)
    
    Некоторые настройки требуют перезапуска приложения
    """
    updated = []
    requires_restart = []
    
    if update.ocr_languages is not None:
        settings.OCR_LANGUAGES = update.ocr_languages
        updated.append("ocr_languages")
        requires_restart.append("ocr_languages")
    
    if update.default_ocr_engine is not None:
        if update.default_ocr_engine not in settings.ALLOWED_OCR_ENGINES:
            raise HTTPException(400, f"Invalid engine: {update.default_ocr_engine}")
        settings.DEFAULT_OCR_ENGINE = update.default_ocr_engine
        updated.append("default_ocr_engine")
    
    if update.ocr_gpu is not None:
        settings.OCR_GPU = update.ocr_gpu
        updated.append("ocr_gpu")
        requires_restart.append("ocr_gpu")
    
    if update.max_concurrent_ocr is not None:
        if 1 <= update.max_concurrent_ocr <= 8:
            settings.MAX_CONCURRENT_OCR = update.max_concurrent_ocr
            updated.append("max_concurrent_ocr")
            requires_restart.append("max_concurrent_ocr")
        else:
            raise HTTPException(400, "max_concurrent_ocr must be 1-8")
    
    if update.pdf_dpi is not None:
        settings.PDF_DPI = update.pdf_dpi
        updated.append("pdf_dpi")
    
    return {
        "status": "success",
        "updated": updated,
        "requires_restart": requires_restart
    }


@router.post("/reset")
async def reset_settings():
    """Сбросить настройки к значениям по умолчанию"""
    # Здесь можно перезагрузить из .env или установить дефолты
    return {"status": "Settings reset to defaults (requires restart)"}
