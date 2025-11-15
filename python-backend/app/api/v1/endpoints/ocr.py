import time
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import SessionLocal
from app.models.file import File as FileModel
from app.services.file_processor import FileProcessor
from app.services.document_service import DocumentService
from app.services.search_service import index_document
from app.services.ocr import get_ocr_manager  # ИЗМЕНЕНО
from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/process/{file_id}")
async def process_file(
    file_id: int,
    mode: str = Query("auto", enum=["auto", "printed", "handwritten"]),
    engine: str = Query("auto", enum=["auto", "paddleocr", "easyocr"]),
    force_ocr: bool = False
):
    """
    Обработать файл через OCR
    
    - **file_id**: ID файла
    - **mode**: режим распознавания
    - **engine**: OCR движок для использования
    - **force_ocr**: использовать OCR даже если есть текст
    """
    db: Session = SessionLocal()
    
    try:
        file_obj = db.query(FileModel).filter(FileModel.id == file_id).first()
        if not file_obj:
            raise HTTPException(status_code=404, detail="File not found")
        
        if file_obj.is_processed and not force_ocr:
            raise HTTPException(status_code=400, detail="File already processed")
        
        if file_obj.mime_type != "application/pdf":
            raise HTTPException(status_code=415, detail="Only PDF supported")
        
        start_time = time.time()
        processor = FileProcessor()
        
        pdf_info = processor.get_pdf_info(file_obj.filepath)
        has_text = pdf_info.get("has_text", False)
        
        use_ocr = force_ocr or not has_text
        
        if use_ocr:
            ocr_manager = get_ocr_manager()
            selected_engine = settings.DEFAULT_OCR_ENGINE if engine == "auto" else engine
            
            logger.info(f"Processing file {file_id} with OCR engine: {selected_engine}")
            
            ocr_result = processor.process_pdf_with_ocr(
                file_obj.filepath,
                ocr_manager,
                engine=selected_engine,
                dpi=300,
                mode=mode
            )
            
            text = ocr_result["text"]
            confidence = ocr_result["confidence"]
            pages = ocr_result["pages"]
            used_engine = selected_engine
            
        else:
            logger.info(f"Extracting embedded text from file {file_id}")
            text = processor.extract_pdf_text(file_obj.filepath)
            confidence = 1.0
            pages = None
            used_engine = "text_extraction"
        
        processing_time = time.time() - start_time
        
        doc_service = DocumentService(db)
        document = doc_service.create_document(
            file_id=file_id,
            text_content=text,
            pages=pages,
            confidence_score=confidence,
            processing_time=processing_time
        )
        
        index_document(document.id, file_obj.filename, text)
        
        file_obj.ocr_mode = f"{used_engine}:{mode}"
        db.commit()
        
        logger.info(f"Processed file {file_id} -> document {document.id}")
        
        return {
            "status": "success",
            "document_id": document.id,
            "page_count": document.page_count,
            "used_ocr": use_ocr,
            "engine": used_engine,
            "confidence": confidence,
            "processing_time": processing_time,
            "text_length": len(text),
        }
    
    except Exception as e:
        logger.exception(f"Failed to process file {file_id}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    finally:
        db.close()


@router.get("/status/{file_id}")
async def get_ocr_status(file_id: int):
    # Этот endpoint без изменений
    db: Session = SessionLocal()
    try:
        file_obj = db.query(FileModel).filter(FileModel.id == file_id).first()
        if not file_obj:
            raise HTTPException(status_code=404, detail="File not found")
        
        doc_service = DocumentService(db)
        document = doc_service.get_by_file_id(file_id)
        
        return {
            "file_id": file_id,
            "filename": file_obj.filename,
            "is_processed": file_obj.is_processed,
            "ocr_mode": file_obj.ocr_mode,
            "document_id": document.id if document else None,
            "processed_at": document.processed_at if document else None,
            "confidence": document.confidence_score if document else None,
        }
    finally:
        db.close()
        