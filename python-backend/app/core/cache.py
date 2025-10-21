"""
Простой in-memory кэш для десктопного приложения
Не требует внешних зависимостей типа Redis
"""
from typing import Dict, Any, Optional, Callable
from functools import lru_cache, wraps
import threading
import time
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheEntry:
    """Запись в кэше с TTL"""
    
    def __init__(self, value: Any, ttl: Optional[int] = None):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl  # время жизни в секундах
    
    def is_expired(self) -> bool:
        """Проверить, истёк ли срок жизни записи"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl


class InMemoryCache:
    """
    Потокобезопасный in-memory кэш для десктопного приложения
    
    Особенности:
    - Потокобезопасность через threading.Lock
    - Поддержка TTL (time-to-live)
    - Автоматическая очистка устаревших записей
    - Ограничение размера кэша
    """
    
    def __init__(self, max_size: int = 128, cleanup_interval: int = 300):
        """
        Args:
            max_size: Максимальный размер кэша
            cleanup_interval: Интервал очистки устаревших записей (секунды)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()
        self._max_size = max_size
        self._cleanup_interval = cleanup_interval
        self._last_cleanup = time.time()
        
        logger.info(f"Initialized InMemoryCache with max_size={max_size}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Получить значение из кэша
        
        Args:
            key: Ключ
            
        Returns:
            Значение или None если ключ не найден или устарел
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                return None
            
            if entry.is_expired():
                del self._cache[key]
                logger.debug(f"Cache expired for key: {key}")
                return None
            
            logger.debug(f"Cache hit for key: {key}")
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Сохранить значение в кэш
        
        Args:
            key: Ключ
            value: Значение
            ttl: Время жизни в секундах (None = бесконечно)
        """
        with self._lock:
            # Проверка размера кэша
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._evict_oldest()
            
            self._cache[key] = CacheEntry(value, ttl)
            logger.debug(f"Cache set for key: {key} (ttl={ttl})")
            
            # Периодическая очистка
            if time.time() - self._last_cleanup > self._cleanup_interval:
                self._cleanup_expired()
    
    def delete(self, key: str) -> bool:
        """
        Удалить ключ из кэша
        
        Args:
            key: Ключ для удаления
            
        Returns:
            True если ключ был удалён
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Cache deleted for key: {key}")
                return True
            return False
    
    def clear(self) -> None:
        """Очистить весь кэш"""
        with self._lock:
            self._cache.clear()
            logger.info("Cache cleared")
    
    def exists(self, key: str) -> bool:
        """Проверить наличие ключа в кэше"""
        return self.get(key) is not None
    
    def size(self) -> int:
        """Получить текущий размер кэша"""
        with self._lock:
            return len(self._cache)
    
    def keys(self) -> list:
        """Получить все ключи в кэше"""
        with self._lock:
            return list(self._cache.keys())
    
    def _evict_oldest(self) -> None:
        """Удалить самую старую запись (LRU)"""
        if not self._cache:
            return
        
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at
        )
        del self._cache[oldest_key]
        logger.debug(f"Evicted oldest cache entry: {oldest_key}")
    
    def _cleanup_expired(self) -> None:
        """Удалить все устаревшие записи"""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        self._last_cleanup = time.time()
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику кэша"""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "keys": list(self._cache.keys())
            }


class OCRCache:
    """
    Специализированный кэш для OCR результатов
    """
    
    def __init__(self, cache: InMemoryCache):
        self.cache = cache
        self.default_ttl = 3600  # 1 час
    
    def get_ocr_result(self, file_hash: str, ocr_mode: str) -> Optional[Dict]:
        """
        Получить закэшированный результат OCR
        
        Args:
            file_hash: Хэш файла
            ocr_mode: Режим OCR ('printed' или 'handwritten')
            
        Returns:
            Результат OCR или None
        """
        key = f"ocr:{file_hash}:{ocr_mode}"
        return self.cache.get(key)
    
    def set_ocr_result(
        self,
        file_hash: str,
        ocr_mode: str,
        result: Dict,
        ttl: Optional[int] = None
    ) -> None:
        """
        Закэшировать результат OCR
        
        Args:
            file_hash: Хэш файла
            ocr_mode: Режим OCR
            result: Результат OCR
            ttl: Время жизни (по умолчанию 1 час)
        """
        key = f"ocr:{file_hash}:{ocr_mode}"
        self.cache.set(key, result, ttl or self.default_ttl)
    
    def invalidate_file(self, file_hash: str) -> None:
        """Удалить все результаты OCR для файла"""
        for mode in ['printed', 'handwritten']:
            key = f"ocr:{file_hash}:{mode}"
            self.cache.delete(key)


def cached(ttl: Optional[int] = None):
    """
    Декоратор для кэширования результатов функций
    
    Args:
        ttl: Время жизни кэша в секундах
        
    Example:
        @cached(ttl=300)
        def expensive_function(arg1, arg2):
            # дорогостоящие вычисления
            return result
    """
    def decorator(func: Callable):
        cache = {}
        lock = threading.Lock()
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Создаём ключ из аргументов
            key = f"{func.__name__}:{args}:{sorted(kwargs.items())}"
            
            with lock:
                if key in cache:
                    entry, timestamp = cache[key]
                    if ttl is None or time.time() - timestamp < ttl:
                        return entry
                
                result = func(*args, **kwargs)
                cache[key] = (result, time.time())
                
                # Ограничение размера кэша
                if len(cache) > 100:
                    oldest_key = min(cache.keys(), key=lambda k: cache[k][1])
                    del cache[oldest_key]
                
                return result
        
        return wrapper
    return decorator


# Глобальный экземпляр кэша
_global_cache: Optional[InMemoryCache] = None


def get_cache() -> InMemoryCache:
    """Получить глобальный экземпляр кэша"""
    global _global_cache
    if _global_cache is None:
        _global_cache = InMemoryCache()
    return _global_cache


def get_ocr_cache() -> OCRCache:
    """Получить OCR кэш"""
    return OCRCache(get_cache())
