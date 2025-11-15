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
from app.services.search_service import ensure_fts_table  # ДОБАВЛЕНО

logger = get_logger(__name__)
file_monitor: FileMonitor | None = None


def _hash_file(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _on_new_file(filepath: str):
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
        logger.info(f"Indexed new file: {filepath}")
        db.close()
    except Exception as e:
        logger.exception(f"Failed to index new file {filepath}: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация при старте
    setup_logging()
    init_db()
    
    # ДОБАВЛЕНО: Инициализация FTS
    ensure_fts_table()

    # Запуск мониторинга папки
    global file_monitor
    file_monitor = FileMonitor(settings.WATCH_FOLDER, _on_new_file)
    file_monitor.start()

    try:
        yield
    finally:
        # Корректное завершение
        if file_monitor:
            file_monitor.stop()


app = FastAPI(
    title="OCR Desktop Manager",
    version="0.1.0",
    lifespan=lifespan,
)

# Разрешим Electron UI с localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:*",
        "http://127.0.0.1:*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роуты API
app.include_router(api_router, prefix="/api/v1")
