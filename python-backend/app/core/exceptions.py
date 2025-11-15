"""
Кастомные исключения для OCR приложения
"""
from typing import Optional, Dict, Any


class AppException(Exception):
    """Базовый класс для всех исключений приложения"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать исключение в словарь"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


# ==================== Файловые исключения ====================

class FileException(AppException):
    """Базовое исключение для файловых операций"""
    pass


class FileNotFoundError(FileException):
    """Файл не найден"""
    
    def __init__(self, filepath: str):
        super().__init__(
            message=f"File not found: {filepath}",
            error_code="FILE_NOT_FOUND",
            details={"filepath": filepath}
        )


class FileFormatError(FileException):
    """Неподдерживаемый формат файла"""
    
    def __init__(self, filepath: str, format: str):
        super().__init__(
            message=f"Unsupported file format: {format}",
            error_code="UNSUPPORTED_FORMAT",
            details={"filepath": filepath, "format": format}
        )


class FileSizeError(FileException):
    """Файл слишком большой"""
    
    def __init__(self, filepath: str, size_mb: float, max_size_mb: int):
        super().__init__(
            message=f"File size ({size_mb}MB) exceeds maximum ({max_size_mb}MB)",
            error_code="FILE_TOO_LARGE",
            details={
                "filepath": filepath,
                "size_mb": size_mb,
                "max_size_mb": max_size_mb
            }
        )


class FileHashError(FileException):
    """Ошибка вычисления хэша файла"""
    
    def __init__(self, filepath: str, reason: str):
        super().__init__(
            message=f"Failed to calculate file hash: {reason}",
            error_code="HASH_ERROR",
            details={"filepath": filepath, "reason": reason}
        )


# ==================== OCR исключения ====================

class OCRException(AppException):
    """Базовое исключение для OCR операций"""
    pass


class OCRInitError(OCRException):
    """Ошибка инициализации OCR движка"""
    
    def __init__(self, engine: str, reason: str):
        super().__init__(
            message=f"Failed to initialize OCR engine '{engine}': {reason}",
            error_code="OCR_INIT_ERROR",
            details={"engine": engine, "reason": reason}
        )


class OCRProcessError(OCRException):
    """Ошибка обработки OCR"""
    
    def __init__(self, filepath: str, reason: str):
        super().__init__(
            message=f"OCR processing failed: {reason}",
            error_code="OCR_PROCESS_ERROR",
            details={"filepath": filepath, "reason": reason}
        )


class OCRTimeoutError(OCRException):
    """Таймаут OCR обработки"""
    
    def __init__(self, filepath: str, timeout_seconds: int):
        super().__init__(
            message=f"OCR processing timed out after {timeout_seconds}s",
            error_code="OCR_TIMEOUT",
            details={"filepath": filepath, "timeout": timeout_seconds}
        )


# ==================== Исключения базы данных ====================

class DatabaseException(AppException):
    """Базовое исключение для операций с БД"""
    pass


class DocumentNotFoundError(DatabaseException):
    """Документ не найден в БД"""
    
    def __init__(self, document_id: int):
        super().__init__(
            message=f"Document with ID {document_id} not found",
            error_code="DOCUMENT_NOT_FOUND",
            details={"document_id": document_id}
        )


class DatabaseConnectionError(DatabaseException):
    """Ошибка подключения к БД"""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"Database connection failed: {reason}",
            error_code="DB_CONNECTION_ERROR",
            details={"reason": reason}
        )


# ==================== Исключения синхронизации ====================

class SyncException(AppException):
    """Базовое исключение для синхронизации"""
    pass


class ServerConnectionError(SyncException):
    """Ошибка подключения к серверу"""
    
    def __init__(self, server_url: str, reason: str):
        super().__init__(
            message=f"Failed to connect to server '{server_url}': {reason}",
            error_code="SERVER_CONNECTION_ERROR",
            details={"server_url": server_url, "reason": reason}
        )


class SyncDataError(SyncException):
    """Ошибка синхронизации данных"""
    
    def __init__(self, document_id: int, reason: str):
        super().__init__(
            message=f"Failed to sync document {document_id}: {reason}",
            error_code="SYNC_DATA_ERROR",
            details={"document_id": document_id, "reason": reason}
        )


# ==================== Исключения конфигурации ====================

class ConfigurationError(AppException):
    """Ошибка конфигурации"""
    
    def __init__(self, setting: str, reason: str):
        super().__init__(
            message=f"Configuration error for '{setting}': {reason}",
            error_code="CONFIG_ERROR",
            details={"setting": setting, "reason": reason}
        )


class FileProcessError(FileException):
    """Ошибка обработки файла"""
    
    def __init__(self, filepath: str, reason: str):
        super().__init__(
            message=f"File processing failed: {reason}",
            error_code="FILE_PROCESS_ERROR",
            details={"filepath": filepath, "reason": reason}
        )