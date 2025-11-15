import logging
import time
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.file import File as FileModel
from app.services.file_processor import FileProcessor
from app.services.document_service import DocumentService
from app.services.search_service import index_document
from app.services.ocr import get_ocr_manager
from app.core.config import settings
from app.api.v1.endpoints.ws import notify_processing_started, notify_processing_completed, notify_processing_failed

logger = logging.getLogger(__name__)


async def process_ocr_task(data: dict):
    """
    Основная функция для обработки OCR задачи из очереди
    
    Args:
        data: Словарь с данными задачи, должен содержать "file_id"
    """
    file_id = data.get("file_id")
    if not file_id:
        logger.error("No file_id in task data")
        return
    
    await notify_processing_started(file_id)
    db: Session = SessionLocal()
    
    try:
        file_obj = db.query(FileModel).filter(FileModel.id == file_id).first()
        if not file_obj:
            logger.error(f"File with id={file_id} not found in DB")
            return
        
        start_time = time.time()
        processor = FileProcessor()
        
        pdf_info = processor.get_pdf_info(file_obj.filepath)
        has_text = pdf_info.get("has_text", False)
        
        use_ocr = not has_text
        
        if use_ocr:
            ocr_manager = get_ocr_manager()
            engine = settings.DEFAULT_OCR_ENGINE
            
            logger.info(f"Processing file {file_id} with OCR engine: {engine}")
            
            ocr_result = processor.process_pdf_with_ocr(
                file_obj.filepath, ocr_manager, engine=engine, dpi=300
            )
            text = ocr_result["text"]
            confidence = ocr_result["confidence"]
            pages = ocr_result["pages"]
            used_engine = engine
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
            processing_time=processing_time,
        )
        
        index_document(document.id, file_obj.filename, text)
        
        file_obj.ocr_mode = used_engine
        db.commit()
        
        await notify_processing_completed(file_id, document.id)
        logger.info(f"Successfully processed file {file_id}, created document {document.id}")
        
    except Exception as e:
        await notify_processing_failed(file_id, str(e))
        logger.exception(f"Failed to process file {file_id} in worker: {e}")
        db.rollback()
    finally:
        db.close()
