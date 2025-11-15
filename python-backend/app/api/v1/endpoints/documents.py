"""
Endpoints для работы с документами
"""
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import SessionLocal
from app.models.document import Document
from app.services.document_service import DocumentService

router = APIRouter()


@router.get("")
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    synced: Optional[bool] = None
):
    """
    Список документов
    
    - **skip**: Пропустить записей
    - **limit**: Максимум записей
    - **synced**: Фильтр по статусу синхронизации
    """
    db: Session = SessionLocal()
    
    try:
        query = db.query(Document)
        
        if synced is not None:
            query = query.filter(Document.is_synced == synced)
        
        docs = query.order_by(Document.id.desc()).offset(skip).limit(limit).all()
        
        return [
            {
                "id": d.id,
                "file_id": d.file_id,
                "page_count": d.page_count,
                "confidence_score": d.confidence_score,
                "processed_at": d.processed_at,
                "processing_time_seconds": d.processing_time_seconds,
                "is_synced": d.is_synced,
                "text_preview": d.text_content[:200] + "..." if len(d.text_content) > 200 else d.text_content
            }
            for d in docs
        ]
    
    finally:
        db.close()


@router.get("/{document_id}")
async def get_document(document_id: int):
    """Получить полный документ"""
    db: Session = SessionLocal()
    
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "id": doc.id,
            "file_id": doc.file_id,
            "text_content": doc.text_content,
            "page_count": doc.page_count,
            "confidence_score": doc.confidence_score,
            "processed_at": doc.processed_at,
            "processing_time_seconds": doc.processing_time_seconds,
            "is_synced": doc.is_synced,
            "needs_sync": doc.needs_sync,
        }
    
    finally:
        db.close()


@router.get("/{document_id}/pages")
async def get_document_pages(document_id: int):
    """Получить страницы документа"""
    db: Session = SessionLocal()
    
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return [
            {
                "page_number": p.page_number,
                "text_content": p.text_content,
                "confidence_score": p.confidence_score,
                "has_boxes": p.bounding_boxes is not None
            }
            for p in doc.pages
        ]
    
    finally:
        db.close()
        