"""
Тест инициализации проекта
"""
import sys
from pathlib import Path

def test_initialization():
    """Проверить инициализацию проекта"""
    
    print("Тестирование инициализации проекта...\n")
    
    # Проверка импортов
    try:
        from app.core.config import settings
        from app.core.cache import InMemoryCache, get_cache
        from app.core.exceptions import AppException
        from app.core.logging import setup_logging
        print("Все модули импортируются успешно")
    except Exception as e:
        print(f"Ошибка импорта: {e}")
        return False
    
    # Проверка настроек
    print(f"\nДиректория приложения: {settings.APP_DATA_DIR}")
    print(f"Папка мониторинга: {settings.WATCH_FOLDER}")
    print(f"База данных: {settings.DATABASE_PATH}")
    print(f"OCR движок: {settings.DEFAULT_OCR_ENGINE}")
    print(f"Локальный сервер: {settings.LOCAL_SERVER_HOST}:{settings.LOCAL_SERVER_PORT}")
    
    # Проверка создания директорий
    required_dirs = [
        settings.APP_DATA_DIR,
        settings.WATCH_FOLDER,
        settings.PROCESSED_FOLDER,
        settings.CACHE_DIR,
        settings.LOGS_DIR,
    ]
    
    print("\nПроверка директорий:")
    for directory in required_dirs:
        exists = directory.exists()
        status = "SUCCESS" if exists else "FAILD"
        print(f"{status} {directory}")
    
    # Проверка кэша
    print("\nТест кэша:")
    cache = get_cache()
    cache.set("test_key", "test_value", ttl=60)
    value = cache.get("test_key")
    if value == "test_value":
        print("Кэш работает корректно")
    else:
        print("Кэш не работает")
    
    # Проверка логирования
    print("\nТест логирования:")
    setup_logging()
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Тестовое сообщение")
    print("Логирование настроено")
    
    print("\nИнициализация проекта завершена успешно!")
    return True

if __name__ == "__main__":
    success = test_initialization()
    sys.exit(0 if success else 1)
    