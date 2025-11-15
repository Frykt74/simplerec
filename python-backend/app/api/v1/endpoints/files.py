"""
Endpoints для управления файлами
"""
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import SessionLocal
from app.models.file import File as FileModel

router = APIRouter()


@router.get("")
async def list_files(
    skip: int = 0,
    limit: int = 50,
    processed: bool = None
):
    """
    Получить список файлов
    
    - **skip**: сколько пропустить
    - **limit**: максимум записей
    - **processed**: фильтр по статусу обработки
    """
    db: Session = SessionLocal()
    
    try:
        query = db.query(FileModel)
        
        # Фильтр по обработке
        if processed is not None:
            query = query.filter(FileModel.is_processed == processed)
        
        files = query.order_by(FileModel.id.desc()).offset(skip).limit(limit).all()
        
        return [
            {
                "id": f.id,
                "filename": f.filename,
                "filepath": f.filepath,
                "file_hash": f.file_hash,
                "file_size": f.file_size,
                "mime_type": f.mime_type,
                "is_processed": f.is_processed,
                "ocr_mode": f.ocr_mode,
                "created_at": f.created_at,
            }
            for f in files
        ]
    
    finally:
        db.close()


@router.get("/{file_id}")
async def get_file(file_id: int):
    """Получить информацию о файле"""
    db: Session = SessionLocal()
    
    try:
        file_obj = db.query(FileModel).filter(FileModel.id == file_id).first()
        if not file_obj:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "id": file_obj.id,
            "filename": file_obj.filename,
            "filepath": file_obj.filepath,
            "file_hash": file_obj.file_hash,
            "file_size": file_obj.file_size,
            "mime_type": file_obj.mime_type,
            "is_processed": file_obj.is_processed,
            "ocr_mode": file_obj.ocr_mode,
            "created_at": file_obj.created_at,
            "updated_at": file_obj.updated_at,
        }
    
    finally:
        db.close()


@router.delete("/{file_id}")
async def delete_file(file_id: int):
    """Удалить файл из БД"""
    db: Session = SessionLocal()
    
    try:
        file_obj = db.query(FileModel).filter(FileModel.id == file_id).first()
        if not file_obj:
            raise HTTPException(status_code=404, detail="File not found")
        
        db.delete(file_obj)
        db.commit()
        
        return {"status": "deleted", "file_id": file_id}
    
    finally:
        db.close()
        