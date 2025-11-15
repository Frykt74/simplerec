"""
Endpoints для статистики и метрик
"""
from fastapi import APIRouter
from sqlalchemy import func
from datetime import datetime, timedelta

from app.db.session import SessionLocal
from app.models.file import File as FileModel
from app.models.document import Document
from app.core.config import settings

router = APIRouter()


@router.get("")
async def get_statistics():
    """Получить общую статистику"""
    db = SessionLocal()
    
    try:
        # Подсчеты
        total_files = db.query(func.count(FileModel.id)).scalar()
        processed_files = db.query(func.count(FileModel.id)).filter(
            FileModel.is_processed == True
        ).scalar()
        total_documents = db.query(func.count(Document.id)).scalar()
        
        # Средняя уверенность
        avg_confidence = db.query(func.avg(Document.confidence_score)).scalar() or 0.0
        
        # Общее время обработки
        total_processing_time = db.query(
            func.sum(Document.processing_time_seconds)
        ).scalar() or 0.0
        
        # Размер базы данных
        db_size = settings.DATABASE_PATH.stat().st_size if settings.DATABASE_PATH.exists() else 0
        
        # Использование папок
        watch_folder_files = len(list(settings.WATCH_FOLDER.glob("*"))) if settings.WATCH_FOLDER.exists() else 0
        
        return {
            "files": {
                "total": total_files,
                "processed": processed_files,
                "pending": total_files - processed_files,
                "in_watch_folder": watch_folder_files
            },
            "documents": {
                "total": total_documents,
                "avg_confidence": round(avg_confidence, 3),
            },
            "processing": {
                "total_time_seconds": round(total_processing_time, 2),
                "avg_time_per_doc": round(total_processing_time / total_documents, 2) if total_documents > 0 else 0
            },
            "storage": {
                "database_size_mb": round(db_size / (1024 * 1024), 2),
                "database_path": str(settings.DATABASE_PATH)
            }
        }
    
    finally:
        db.close()


@router.get("/recent")
async def get_recent_activity(hours: int = 24):
    """Получить активность за последние N часов"""
    db = SessionLocal()
    
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        
        recent_files = db.query(func.count(FileModel.id)).filter(
            FileModel.created_at >= since
        ).scalar()
        
        recent_docs = db.query(func.count(Document.id)).filter(
            Document.processed_at >= since
        ).scalar()
        
        return {
            "period_hours": hours,
            "files_added": recent_files,
            "documents_created": recent_docs
        }
    
    finally:
        db.close()
        