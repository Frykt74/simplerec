"""
Утилиты для хэширования файлов
"""
import hashlib


def hash_file(filepath: str) -> str:
    """
    Вычислить SHA256 хэш файла
    
    Args:
        filepath: Путь к файлу
        
    Returns:
        Хэш в hex формате
    """
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
