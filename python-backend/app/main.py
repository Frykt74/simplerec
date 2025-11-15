from contextlib import asynccontextmanager
from pathlib import Path
import hashlib
import mimetypes
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.file import File as FileModel
from app.services.file_monitor import FileMonitor
from app.services.search_service import ensure_fts_table
from app.workers.queue_manager import QueueManager
from app.workers.ocr_worker import process_ocr_task

logger = get_logger(__name__)
file_monitor: FileMonitor | None = None
queue_manager: QueueManager | None = None


def _hash_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


async def _on_new_file(filepath: str):
    global queue_manager
    try:
        db = SessionLocal()
        stat = os.stat(filepath)
        mime = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
        file_hash = _hash_file(filepath)

        exists = db.query(FileModel).filter(FileModel.file_hash == file_hash).first()
        if exists:
            logger.info(f"Skip duplicate: {filepath}")
            db.close()
            return

        rec = FileModel(
            filename=Path(filepath).name,
            filepath=filepath,
            file_hash=file_hash,
            file_size=stat.st_size,
            mime_type=mime,
            is_processed=False,
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        file_id = rec.id
        
        logger.info(f"Indexed new file: {filepath} (id={file_id})")
        db.close()
        
        if queue_manager:
            await queue_manager.add_task({"file_id": file_id})
        
    except Exception as e:
        logger.exception(f"Failed to index new file {filepath}: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global file_monitor, queue_manager
    
    setup_logging()
    init_db()
    ensure_fts_table()
    
    queue_manager = QueueManager(worker_func=process_ocr_task, num_workers=settings.MAX_CONCURRENT_OCR)
    await queue_manager.start()
    
    file_monitor = FileMonitor(settings.WATCH_FOLDER, _on_new_file)
    file_monitor.start()

    try:
        yield
    finally:
        if file_monitor:
            file_monitor.stop()
        if queue_manager:
            await queue_manager.stop()


app = FastAPI(
    title="OCR Desktop Manager",
    version="1.0.0-mvp",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
