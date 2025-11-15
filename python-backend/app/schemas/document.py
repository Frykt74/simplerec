from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class PageBase(BaseModel):
    page_number: int
    text_content: Optional[str] = None
    confidence_score: Optional[float] = None


class DocumentBase(BaseModel):
    text_content: str
    confidence_score: Optional[float] = None
    page_count: int


class DocumentCreate(DocumentBase):
    file_id: int


class DocumentUpdate(BaseModel):
    is_synced: Optional[bool] = None
    needs_sync: Optional[bool] = None


class DocumentInDB(DocumentBase):
    id: int
    file_id: int
    processed_at: datetime
    is_synced: bool
    
    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(DocumentInDB):
    text_preview: Optional[str] = None
    