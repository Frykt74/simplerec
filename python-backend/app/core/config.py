"""
Конфигурация для десктопного OCR приложения
"""
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """Настройки приложения для десктопного режима"""
    
    # ==================== Основные настройки ====================
    APP_NAME: str = "OCR Desktop Manager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # ==================== Локальные пути ====================
    # Базовая директория в домашней папке пользователя
    APP_DATA_DIR: Path = Field(
        default_factory=lambda: Path.home() / ".ocr-app"
    )
    
    @property
    def WATCH_FOLDER(self) -> Path:
        """Папка для мониторинга новых файлов"""
        return self.APP_DATA_DIR / "watch"
    
    @property
    def PROCESSED_FOLDER(self) -> Path:
        """Папка для обработанных файлов"""
        return self.APP_DATA_DIR / "processed"
    
    @property
    def DATABASE_PATH(self) -> Path:
        """Путь к SQLite базе данных"""
        return self.APP_DATA_DIR / "database" / "local.db"
    
    @property
    def CACHE_DIR(self) -> Path:
        """Папка для кэша OCR моделей"""
        return self.APP_DATA_DIR / "cache"
    
    @property
    def LOGS_DIR(self) -> Path:
        """Папка для логов"""
        return self.APP_DATA_DIR / "logs"
    
    # ==================== OCR настройки ====================
    DEFAULT_OCR_ENGINE: str = Field(
        default="paddleocr",
        description="Движок OCR по умолчанию (paddleocr или easyocr)"
    )
    OCR_LANGUAGES: List[str] = Field(
        default=["en", "ru"],
        description="Языки для распознавания"
    )
    OCR_GPU: bool = Field(
        default=False,
        description="Использовать GPU для OCR"
    )
    MAX_CONCURRENT_OCR: int = Field(
        default=2,
        description="Максимальное количество одновременных OCR задач"
    )
    OCR_CONFIDENCE_THRESHOLD: float = Field(
        default=0.5,
        description="Минимальный порог уверенности OCR"
    )
    
    # ==================== Настройки обработки файлов ====================
    SUPPORTED_FORMATS: List[str] = Field(
        default=["pdf", "png", "jpg", "jpeg", "tiff", "bmp"],
        description="Поддерживаемые форматы файлов"
    )
    MAX_FILE_SIZE_MB: int = Field(
        default=50,
        description="Максимальный размер файла в МБ"
    )
    PDF_DPI: int = Field(
        default=300,
        description="DPI для конвертации PDF в изображения"
    )
    
    # ==================== Серверная синхронизация ====================
    SERVER_ENABLED: bool = Field(
        default=False,
        description="Включить синхронизацию с сервером"
    )
    SERVER_URL: str = Field(
        default="",
        description="URL корпоративного сервера"
    )
    OPENSEARCH_URL: str = Field(
        default="",
        description="URL OpenSearch для полнотекстового поиска"
    )
    OPENSEARCH_USERNAME: Optional[str] = Field(
        default=None,
        description="Имя пользователя OpenSearch"
    )
    OPENSEARCH_PASSWORD: Optional[str] = Field(
        default=None,
        description="Пароль OpenSearch"
    )
    SYNC_INTERVAL_MINUTES: int = Field(
        default=30,
        description="Интервал синхронизации в минутах"
    )
    BATCH_SIZE: int = Field(
        default=50,
        description="Размер batch для выгрузки на сервер"
    )
    SYNC_RETRY_ATTEMPTS: int = Field(
        default=3,
        description="Количество попыток повторной синхронизации"
    )
    
    # ==================== Локальный FastAPI сервер ====================
    LOCAL_SERVER_HOST: str = Field(
        default="127.0.0.1",
        description="Host локального API сервера"
    )
    LOCAL_SERVER_PORT: int = Field(
        default=8765,
        description="Port локального API сервера"
    )
    RELOAD: bool = Field(
        default=False,
        description="Auto-reload для разработки"
    )
    
    # ==================== База данных ====================
    @property
    def DATABASE_URL(self) -> str:
        """URL для подключения к SQLite"""
        return f"sqlite:///{self.DATABASE_PATH}"
    
    DB_ECHO: bool = Field(
        default=False,
        description="Выводить SQL запросы в лог"
    )
    
    # ==================== Логирование ====================
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Уровень логирования (DEBUG, INFO, WARNING, ERROR)"
    )
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Формат логов"
    )
    LOG_MAX_BYTES: int = Field(
        default=10485760,  # 10 MB
        description="Максимальный размер лог-файла"
    )
    LOG_BACKUP_COUNT: int = Field(
        default=5,
        description="Количество резервных копий логов"
    )
    
    # ==================== Идентификация ====================
    WORKSTATION_ID: Optional[str] = Field(
        default=None,
        description="Уникальный ID рабочей станции"
    )
    USER_ID: Optional[str] = Field(
        default=None,
        description="ID пользователя"
    )
    
    # ==================== Кэширование ====================
    CACHE_ENABLED: bool = Field(
        default=True,
        description="Включить in-memory кэш"
    )
    CACHE_MAX_SIZE: int = Field(
        default=128,
        description="Максимальный размер кэша"
    )
    
    # ==================== Валидаторы ====================
    @validator("DEFAULT_OCR_ENGINE")
    def validate_ocr_engine(cls, v):
        """Проверка корректности OCR движка"""
        allowed = ["paddleocr", "easyocr"]
        if v not in allowed:
            raise ValueError(f"OCR engine must be one of {allowed}")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Проверка уровня логирования"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v
    
    @validator("MAX_CONCURRENT_OCR")
    def validate_max_concurrent(cls, v):
        """Проверка количества одновременных задач"""
        if v < 1 or v > 8:
            raise ValueError("MAX_CONCURRENT_OCR must be between 1 and 8")
        return v
    
    # ==================== Конфигурация Pydantic ====================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    def create_directories(self) -> None:
        """Создать все необходимые директории"""
        directories = [
            self.APP_DATA_DIR,
            self.WATCH_FOLDER,
            self.PROCESSED_FOLDER,
            self.DATABASE_PATH.parent,
            self.CACHE_DIR,
            self.LOGS_DIR,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_workstation_id(self) -> str:
        """Получить или создать ID рабочей станции"""
        if self.WORKSTATION_ID:
            return self.WORKSTATION_ID
        
        import socket
        import hashlib
        hostname = socket.gethostname()
        return hashlib.md5(hostname.encode()).hexdigest()[:16]

ALLOWED_OCR_ENGINES: List[str] = Field(
        default=["paddleocr", "easyocr"],
        description="Разрешенные OCR движки"
    )

# Глобальный экземпляр настроек
settings = Settings()

# Создать директории при импорте
settings.create_directories()