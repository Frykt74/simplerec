"""
Endpoints для OCR обработки
"""
import time
from fastapi import APIRouter, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import SessionLocal
from app.models.file import File as FileModel
from app.services.file_processor import FileProcessor
from app.services.document_service import DocumentService
from app.services.search_service import index_document
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/process/{file_id}")
async def process_file(
    file_id: int,
    mode: str = "auto",  # auto, printed, handwritten
    background_tasks: BackgroundTasks = None
):
    """
    Обработать файл через OCR
    
    - **file_id**: ID файла из таблицы files
    - **mode**: режим OCR (auto, printed, handwritten)
    
    Возвращает информацию о созданном документе
    """
    db: Session = SessionLocal()
    
    try:
        # Получить файл
        file_obj = db.query(FileModel).filter(FileModel.id == file_id).first()
        if not file_obj:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Проверить что еще не обработан
        if file_obj.is_processed:
            raise HTTPException(status_code=400, detail="File already processed")
        
        # Только PDF пока
        if file_obj.mime_type != "application/pdf":
            raise HTTPException(
                status_code=415,
                detail="Only PDF files supported in current version"
            )
        
        # Обработка
        start_time = time.time()
        
        # Пытаемся извлечь встроенный текст
        processor = FileProcessor()
        text = processor.extract_pdf_text(file_obj.filepath)
        
        # Получить информацию о PDF
        pdf_info = processor.get_pdf_info(file_obj.filepath)
        
        processing_time = time.time() - start_time
        
        # Сохранить документ
        doc_service = DocumentService(db)
        document = doc_service.create_document(
            file_id=file_id,
            text_content=text,
            confidence_score=1.0 if pdf_info.get("has_text") else 0.0,
            processing_time=processing_time
        )
        
        # Индексировать в FTS
        index_document(document.id, file_obj.filename, text)
        
        logger.info(f"Processed file {file_id} -> document {document.id}")
        
        return {
            "status": "success",
            "document_id": document.id,
            "page_count": document.page_count,
            "has_text": pdf_info.get("has_text", False),
            "processing_time": processing_time,
            "text_length": len(text),
        }
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.exception(f"Failed to process file {file_id}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    finally:
        db.close()


@router.get("/status/{file_id}")
async def get_ocr_status(file_id: int):
    """
    Получить статус обработки файла
    """
    db: Session = SessionLocal()
    
    try:
        file_obj = db.query(FileModel).filter(FileModel.id == file_id).first()
        if not file_obj:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Получить документ если обработан
        doc_service = DocumentService(db)
        document = doc_service.get_by_file_id(file_id)
        
        return {
            "file_id": file_id,
            "filename": file_obj.filename,
            "is_processed": file_obj.is_processed,
            "ocr_mode": file_obj.ocr_mode,
            "document_id": document.id if document else None,
            "processed_at": document.processed_at if document else None,
        }
    
    finally:
        db.close()
        