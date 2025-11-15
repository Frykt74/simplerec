"""
Endpoints для загрузки файлов напрямую через API
"""
import shutil
import hashlib
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def _hash_file(filepath: str) -> str:
    """Вычислить SHA256 хэш файла"""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    """
    Загрузить файл для обработки
    
    Файл будет сохранен в watch folder и автоматически обработан
    """
    # Проверка формата
    file_ext = Path(file.filename).suffix.lower().lstrip(".")
    if file_ext not in settings.SUPPORTED_FORMATS:
        raise HTTPException(
            400,
            f"Unsupported format: {file_ext}. Supported: {settings.SUPPORTED_FORMATS}"
        )
    
    # Сохранить во временную директорию, затем переместить в watch
    try:
        temp_path = settings.WATCH_FOLDER / f"_uploading_{file.filename}"
        final_path = settings.WATCH_FOLDER / file.filename
        
        # Записать файл
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Переместить (это вызовет событие file monitor)
        temp_path.rename(final_path)
        
        logger.info(f"File uploaded: {final_path}")
        
        return {
            "status": "success",
            "filename": file.filename,
            "path": str(final_path),
            "message": "File uploaded and will be processed automatically"
        }
    
    except Exception as e:
        logger.exception(f"Failed to upload file: {e}")
        raise HTTPException(500, f"Upload failed: {str(e)}")
    