from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class FileBase(BaseModel):
    filename: str
    filepath: str
    mime_type: str
    file_size: int
    file_hash: str


class FileCreate(FileBase):
    pass


class FileUpdate(BaseModel):
    is_processed: Optional[bool] = None
    ocr_mode: Optional[str] = None


class FileInDB(FileBase):
    id: int
    is_processed: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class FileResponse(FileInDB):
    pass
