"""
Полнотекстовый поиск (FTS5)
"""
from typing import List, Dict
from sqlalchemy import text
from app.db.session import SessionLocal
import logging

logger = logging.getLogger(__name__)


def ensure_fts_table():
    """
    Создать FTS5 виртуальную таблицу если не существует
    """
    db = SessionLocal()
    try:
        db.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts
            USING fts5(
                document_id UNINDEXED,
                filename,
                text_content,
                tokenize='unicode61 remove_diacritics 1'
            );
        """))
        db.commit()
        logger.info("FTS table initialized")
    except Exception as e:
        logger.error(f"Failed to create FTS table: {e}")
        db.rollback()
    finally:
        db.close()


def index_document(document_id: int, filename: str, text_content: str):
    """
    Добавить документ в FTS индекс
    
    Args:
        document_id: ID документа
        filename: Имя файла
        text_content: Текст для индексации
    """
    db = SessionLocal()
    try:
        db.execute(text("""
            INSERT INTO documents_fts(document_id, filename, text_content)
            VALUES(:doc_id, :fname, :text)
        """), {
            "doc_id": document_id,
            "fname": filename,
            "text": text_content or ""
        })
        db.commit()
        logger.info(f"Indexed document {document_id} in FTS")
    except Exception as e:
        logger.error(f"Failed to index document {document_id}: {e}")
        db.rollback()
    finally:
        db.close()


def search(query: str, limit: int = 10) -> List[Dict]:
    """
    Поиск документов по тексту
    
    Args:
        query: Поисковый запрос
        limit: Максимальное количество результатов
        
    Returns:
        Список документов с сниппетами
    """
    db = SessionLocal()
    try:
        results = db.execute(text("""
            SELECT 
                document_id,
                filename,
                snippet(documents_fts, 2, '<mark>', '</mark>', '...', 32) AS snippet
            FROM documents_fts
            WHERE documents_fts MATCH :query
            ORDER BY rank
            LIMIT :limit
        """), {
            "query": query,
            "limit": limit
        }).fetchall()
        
        return [
            {
                "document_id": row[0],
                "filename": row[1],
                "snippet": row[2]
            }
            for row in results
        ]
    
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return []
    
    finally:
        db.close()


def delete_from_index(document_id: int):
    """Удалить документ из FTS индекса"""
    db = SessionLocal()
    try:
        db.execute(text("""
            DELETE FROM documents_fts
            WHERE document_id = :doc_id
        """), {"doc_id": document_id})
        db.commit()
        logger.info(f"Deleted document {document_id} from FTS index")
    except Exception as e:
        logger.error(f"Failed to delete from FTS: {e}")
        db.rollback()
    finally:
        db.close()
        