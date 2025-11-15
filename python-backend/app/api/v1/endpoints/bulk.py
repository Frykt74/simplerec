"""
Endpoints для массовых операций
"""
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

from app.db.session import SessionLocal
from app.models.file import File as FileModel
from app.models.document import Document
from app.services.document_service import DocumentService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class BulkDeleteRequest(BaseModel):
    file_ids: List[int]


class BulkReprocessRequest(BaseModel):
    file_ids: List[int]
    force: bool = False


@router.delete("/files")
async def bulk_delete_files(request: BulkDeleteRequest):
    """Удалить несколько файлов"""
    db = SessionLocal()
    
    try:
        deleted = []
        not_found = []
        
        for file_id in request.file_ids:
            file_obj = db.query(FileModel).filter(FileModel.id == file_id).first()
            if file_obj:
                db.delete(file_obj)
                deleted.append(file_id)
            else:
                not_found.append(file_id)
        
        db.commit()
        
        return {
            "status": "success",
            "deleted": deleted,
            "not_found": not_found,
            "total_deleted": len(deleted)
        }
    
    except Exception as e:
        db.rollback()
        logger.exception(f"Bulk delete failed: {e}")
        raise HTTPException(500, f"Bulk delete failed: {str(e)}")
    
    finally:
        db.close()


@router.post("/reprocess")
async def bulk_reprocess_files(request: BulkReprocessRequest):
    """Переобработать несколько файлов"""
    db = SessionLocal()
    
    try:
        queued = []
        skipped = []
        
        for file_id in request.file_ids:
            file_obj = db.query(FileModel).filter(FileModel.id == file_id).first()
            if not file_obj:
                skipped.append({"file_id": file_id, "reason": "not_found"})
                continue
            
            if file_obj.is_processed and not request.force:
                skipped.append({"file_id": file_id, "reason": "already_processed"})
                continue
            
            # Сбросить статус и добавить в очередь
            file_obj.is_processed = False
            queued.append(file_id)
            # TODO: Добавить в очередь через queue_manager
        
        db.commit()
        
        return {
            "status": "success",
            "queued": queued,
            "skipped": skipped,
            "total_queued": len(queued)
        }
    
    except Exception as e:
        db.rollback()
        logger.exception(f"Bulk reprocess failed: {e}")
        raise HTTPException(500, str(e))
    
    finally:
        db.close()


@router.get("/pending")
async def get_pending_files():
    """Получить список файлов ожидающих обработки"""
    db = SessionLocal()
    
    try:
        pending = db.query(FileModel).filter(
            FileModel.is_processed == False
        ).all()
        
        return {
            "pending": [
                {
                    "id": f.id,
                    "filename": f.filename,
                    "created_at": f.created_at
                }
                for f in pending
            ],
            "total": len(pending)
        }
    
    finally:
        db.close()
        