"""
Утилиты для очистки и обслуживания хранилища
"""
import logging
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import func

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.file import File as FileModel
from app.models.document import Document

logger = logging.getLogger(__name__)


def cleanup_old_files(days: int = 30) -> dict:
    """
    Удалить файлы старше N дней
    
    Args:
        days: Возраст файлов в днях
        
    Returns:
        Статистика удаления
    """
    db = SessionLocal()
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    try:
        old_files = db.query(FileModel).filter(
            FileModel.created_at < cutoff_date
        ).all()
        
        deleted_count = 0
        failed_count = 0
        
        for file_obj in old_files:
            try:
                # Удалить физический файл
                file_path = Path(file_obj.filepath)
                if file_path.exists():
                    file_path.unlink()
                
                # Удалить из БД (каскадно удалятся документы)
                db.delete(file_obj)
                deleted_count += 1
                
            except Exception as e:
                logger.error(f"Failed to delete file {file_obj.id}: {e}")
                failed_count += 1
        
        db.commit()
        
        result = {
            "deleted": deleted_count,
            "failed": failed_count,
            "cutoff_date": cutoff_date.isoformat()
        }
        
        logger.info(f"Cleanup completed: {result}")
        return result
        
    finally:
        db.close()


def vacuum_database() -> dict:
    """
    Оптимизировать базу данных (VACUUM для SQLite)
    """
    db = SessionLocal()
    
    try:
        # Размер до
        db_path = settings.DATABASE_PATH
        size_before = db_path.stat().st_size
        
        # VACUUM
        db.execute("VACUUM")
        db.commit()
        
        # Размер после
        size_after = db_path.stat().st_size
        
        result = {
            "size_before_mb": round(size_before / (1024**2), 2),
            "size_after_mb": round(size_after / (1024**2), 2),
            "saved_mb": round((size_before - size_after) / (1024**2), 2)
        }
        
        logger.info(f"Database vacuumed: {result}")
        return result
        
    finally:
        db.close()


def cleanup_orphaned_files() -> dict:
    """
    Удалить файлы без записей в БД
    """
    watch_folder = settings.WATCH_FOLDER
    processed_folder = settings.PROCESSED_FOLDER
    
    db = SessionLocal()
    
    try:
        # Получить все пути из БД
        db_paths = {f.filepath for f in db.query(FileModel.filepath).all()}
        
        deleted_count = 0
        
        # Проверить watch folder
        for file_path in watch_folder.glob("*"):
            if file_path.is_file() and str(file_path) not in db_paths:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted orphaned file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete {file_path}: {e}")
        
        return {"deleted_orphaned": deleted_count}
        
    finally:
        db.close()


def get_storage_stats() -> dict:
    """Получить статистику использования хранилища"""
    db = SessionLocal()
    
    try:
        total_files = db.query(func.count(FileModel.id)).scalar()
        total_size = db.query(func.sum(FileModel.file_size)).scalar() or 0
        
        db_size = settings.DATABASE_PATH.stat().st_size if settings.DATABASE_PATH.exists() else 0
        
        return {
            "files": {
                "total": total_files,
                "total_size_mb": round(total_size / (1024**2), 2)
            },
            "database": {
                "size_mb": round(db_size / (1024**2), 2),
                "path": str(settings.DATABASE_PATH)
            },
            "folders": {
                "watch": str(settings.WATCH_FOLDER),
                "processed": str(settings.PROCESSED_FOLDER),
                "cache": str(settings.CACHE_DIR)
            }
        }
        
    finally:
        db.close()
        