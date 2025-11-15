
"""
Endpoints для поиска
"""
from fastapi import APIRouter, Query
from typing import List, Dict

from app.services.search_service import search as fts_search

router = APIRouter()


@router.get("")
async def search_documents(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    limit: int = Query(10, ge=1, le=100, description="Максимум результатов")
) -> List[Dict]:
    """
    Полнотекстовый поиск по документам
    
    - **q**: поисковый запрос (минимум 2 символа)
    - **limit**: максимальное количество результатов
    """
    results = fts_search(q, limit)
    return results
