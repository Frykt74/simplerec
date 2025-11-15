"""
Сервис для работы с документами
"""
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_page import DocumentPage
from app.models.file import File as FileModel


class DocumentService:
    """Управление документами и их страницами"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_document(
        self,
        file_id: int,
        text_content: str,
        pages: Optional[List[Dict]] = None,
        confidence_score: Optional[float] = None,
        processing_time: Optional[float] = None
    ) -> Document:
        """
        Создать документ с результатами OCR
        
        Args:
            file_id: ID файла
            text_content: Распознанный текст
            pages: Список страниц с текстом и координатами
            confidence_score: Средняя уверенность распознавания
            processing_time: Время обработки в секундах
        
        Returns:
            Созданный документ
        """
        # Подсчет страниц
        page_count = len(pages) if pages else max(1, text_content.count("\f") + 1)
        
        # Создание документа
        doc = Document(
            file_id=file_id,
            text_content=text_content or "",
            confidence_score=confidence_score,
            page_count=page_count,
            processed_at=datetime.utcnow(),
            processing_time_seconds=processing_time,
            is_synced=False,
            needs_sync=True,
        )
        
        self.db.add(doc)
        self.db.flush()  # Получить ID документа
        
        # Создание страниц
        if pages:
            for page_data in pages:
                page = DocumentPage(
                    document_id=doc.id,
                    page_number=page_data.get("page_number", 0),
                    text_content=page_data.get("text", ""),
                    confidence_score=page_data.get("confidence"),
                    bounding_boxes=page_data.get("boxes"),
                )
                self.db.add(page)
        
        # Обновить статус файла
        file_obj = self.db.query(FileModel).get(file_id)
        if file_obj:
            file_obj.is_processed = True
            file_obj.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(doc)
        
        return doc
    
    def get_by_id(self, document_id: int) -> Optional[Document]:
        """Получить документ по ID"""
        return self.db.query(Document).filter(Document.id == document_id).first()
    
    def get_by_file_id(self, file_id: int) -> Optional[Document]:
        """Получить документ по ID файла"""
        return self.db.query(Document).filter(Document.file_id == file_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Document]:
        """Получить список документов"""
        return (
            self.db.query(Document)
            .order_by(Document.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def delete(self, document_id: int) -> bool:
        """Удалить документ"""
        doc = self.get_by_id(document_id)
        if doc:
            self.db.delete(doc)
            self.db.commit()
            return True
        return False
