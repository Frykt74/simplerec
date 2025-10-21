# python-backend/app/core/logging.py

"""
Настройка логирования для десктопного приложения
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from app.core.config import settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> None:
    """
    Настройка системы логирования
    
    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
        log_file: Путь к файлу лога (по умолчанию в LOGS_DIR)
    """
    # Определяем уровень логирования
    level = log_level or settings.LOG_LEVEL
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Определяем путь к лог-файлу
    if log_file is None:
        log_file = settings.LOGS_DIR / "ocr_app.log"
    
    # Создаём папку для логов если не существует
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Форматирование логов
    formatter = logging.Formatter(
        fmt=settings.LOG_FORMAT,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Детальный форматтер для файлов
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - '
            '%(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Очистка существующих handlers
    root_logger.handlers.clear()
    
    # ===== Console Handler =====
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # ===== File Handler (Rotating) =====
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # ===== Error File Handler =====
    error_log_file = settings.LOGS_DIR / "errors.log"
    error_handler = RotatingFileHandler(
        filename=error_log_file,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Логирование сторонних библиотек
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("watchdog").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    # Стартовое сообщение
    logging.info("=" * 60)
    logging.info(f"Logging initialized - Level: {level}")
    logging.info(f"Log file: {log_file}")
    logging.info(f"Error log: {error_log_file}")
    logging.info("=" * 60)


def get_logger(name: str) -> logging.Logger:
    """
    Получить логгер для модуля
    
    Args:
        name: Имя модуля (обычно __name__)
        
    Returns:
        Настроенный логгер
    """
    return logging.getLogger(name)
