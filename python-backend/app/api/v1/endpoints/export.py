"""
Endpoints для экспорта результатов
"""
from fastapi import APIRouter, HTTPException, Response
from typing import List, Optional
import json
import csv
import io

from app.db.session import SessionLocal
from app.models.document import Document

router = APIRouter()


@router.get("/documents/txt/{document_id}")
async def export_document_txt(document_id: int):
    """Экспортировать документ в TXT"""
    db = SessionLocal()
    
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(404, "Document not found")
        
        return Response(
            content=doc.text_content,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename=document_{document_id}.txt"
            }
        )
    
    finally:
        db.close()


@router.get("/documents/json")
async def export_documents_json(
    skip: int = 0,
    limit: int = 100,
    min_confidence: Optional[float] = None
):
    """Экспортировать документы в JSON"""
    db = SessionLocal()
    
    try:
        query = db.query(Document)
        
        if min_confidence is not None:
            query = query.filter(Document.confidence_score >= min_confidence)
        
        docs = query.offset(skip).limit(limit).all()
        
        data = [
            {
                "id": d.id,
                "file_id": d.file_id,
                "text_content": d.text_content,
                "confidence_score": d.confidence_score,
                "page_count": d.page_count,
                "processed_at": d.processed_at.isoformat()
            }
            for d in docs
        ]
        
        return Response(
            content=json.dumps(data, ensure_ascii=False, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=documents.json"}
        )
    
    finally:
        db.close()


@router.get("/documents/csv")
async def export_documents_csv(skip: int = 0, limit: int = 100):
    """Экспортировать документы в CSV"""
    db = SessionLocal()
    
    try:
        docs = db.query(Document).offset(skip).limit(limit).all()
        
        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["id", "file_id", "page_count", "confidence_score", "text_preview"]
        )
        writer.writeheader()
        
        for d in docs:
            writer.writerow({
                "id": d.id,
                "file_id": d.file_id,
                "page_count": d.page_count,
                "confidence_score": d.confidence_score,
                "text_preview": d.text_content[:200]
            })
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=documents.csv"}
        )
    
    finally:
        db.close()
        