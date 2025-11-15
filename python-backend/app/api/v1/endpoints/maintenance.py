
from fastapi import APIRouter
from app.utils.cleanup import (
    cleanup_old_files, vacuum_database,
    cleanup_orphaned_files, get_storage_stats
)

router = APIRouter()


@router.post("/cleanup")
async def cleanup(days: int = 30):
    """Очистить старые файлы"""
    return cleanup_old_files(days)


@router.post("/vacuum")
async def vacuum():
    """Оптимизировать базу данных"""
    return vacuum_database()


@router.post("/cleanup-orphaned")
async def cleanup_orphans():
    """Удалить файлы без записей в БД"""
    return cleanup_orphaned_files()


@router.get("/storage")
async def storage_stats():
    """Статистика хранилища"""
    return get_storage_stats()
