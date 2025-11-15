from contextlib import asynccontextmanager
from pathlib import Path
import hashlib
import mimetypes
import os
import signal

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
from app.api.v1.endpoints import ws
from app.utils.hash_utils import hash_file

logger = get_logger(__name__)
file_monitor: FileMonitor | None = None
queue_manager: QueueManager | None = None


async def _on_new_file(filepath: str):
    global queue_manager
    try:
        db = SessionLocal()
        stat = os.stat(filepath)
        mime = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
        file_hash = hash_file(filepath)

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
    
    logger.info("=" * 60)
    logger.info("Starting OCR Desktop Manager...")
    logger.info("=" * 60)
    
    setup_logging()
    init_db()
    ensure_fts_table()
    
    # Запуск очереди обработки
    queue_manager = QueueManager(
        worker_func=process_ocr_task,
        num_workers=settings.MAX_CONCURRENT_OCR
    )
    await queue_manager.start()
    logger.info(f"Queue manager started with {settings.MAX_CONCURRENT_OCR} workers")
    
    # Запуск мониторинга файлов
    file_monitor = FileMonitor(settings.WATCH_FOLDER, _on_new_file)
    file_monitor.start()
    logger.info(f"File monitor started: {settings.WATCH_FOLDER}")
    
    def signal_handler(signum, frame):
        """Обработчик сигналов завершения"""
        sig_name = signal.Signals(signum).name
        logger.warning(f"Received signal {sig_name} ({signum}), initiating graceful shutdown...")
    
    # Регистрация обработчиков сигналов
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # kill
    
    logger.info("=" * 60)
    logger.info("OCR Desktop Manager is ready!")
    logger.info(f"API Documentation: http://{settings.LOCAL_SERVER_HOST}:{settings.LOCAL_SERVER_PORT}/api/docs")
    logger.info(f"Watch folder: {settings.WATCH_FOLDER}")
    logger.info("=" * 60)

    try:
        yield
    finally:
        logger.info("=" * 60)
        logger.info("Shutting down OCR Desktop Manager...")
        logger.info("=" * 60)
        
        if file_monitor:
            logger.info("Stopping file monitor...")
            file_monitor.stop()
            logger.info("File monitor stopped")
        
        if queue_manager:
            logger.info("Stopping queue manager...")
            await queue_manager.stop()
            logger.info("Queue manager stopped")
        
        logger.info("=" * 60)
        logger.info("Shutdown complete. Goodbye!")
        logger.info("=" * 60)


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
app.include_router(ws.router, prefix="/api/v1/ws", tags=["websocket"])

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs",
        "health": "/api/v1/health"
    }
