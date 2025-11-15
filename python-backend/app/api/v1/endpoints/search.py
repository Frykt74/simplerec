from fastapi import APIRouter, Query
from typing import List, Dict, Optional
from datetime import datetime

from app.services.search_service import search as fts_search
from app.db.session import SessionLocal
from app.models.document import Document
from sqlalchemy import and_

router = APIRouter()


@router.get("")
async def search_documents(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    limit: int = Query(10, ge=1, le=100),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0)
) -> List[Dict]:
    """
    Полнотекстовый поиск
    
    - **q**: Запрос
    - **limit**: Максимум результатов
    - **min_confidence**: Минимальная уверенность OCR
    """
    results = fts_search(q, limit)
    
    # Если фильтр по confidence - дополнительная фильтрация
    if min_confidence is not None:
        db = SessionLocal()
        try:
            filtered = []
            for r in results:
                doc = db.query(Document).get(r["document_id"])
                if doc and (doc.confidence_score or 0) >= min_confidence:
                    r["confidence"] = doc.confidence_score
                    filtered.append(r)
            return filtered
        finally:
            db.close()
    
    return results
