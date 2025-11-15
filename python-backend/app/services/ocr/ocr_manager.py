"""
Менеджер для управления несколькими OCR-движками
"""
import logging
from typing import Dict, Optional

from app.services.ocr.base import BaseOCR
from app.services.ocr.paddleocr_service import PaddleOCRService
from app.services.ocr.easyocr_service import EasyOCRService
from app.core.config import settings

logger = logging.getLogger(__name__)


class OCRManager:
    """Ленивая загрузка и управление OCR-движками"""
    
    def __init__(self):
        self._engines: Dict[str, Optional[BaseOCR]] = {
            "paddleocr": None,
            "easyocr": None,
        }
    
    def _get_engine(self, engine_name: str) -> BaseOCR:
        """
        Ленивая загрузка и получение экземпляра OCR-движка
        
        Args:
            engine_name: "paddleocr" или "easyocr"
            
        Returns:
            Экземпляр OCR-сервиса
        """
        if engine_name not in settings.ALLOWED_OCR_ENGINES:
            raise ValueError(f"Unknown OCR engine: {engine_name}")
        
        # Ленивая загрузка
        if self._engines.get(engine_name) is None:
            logger.info(f"Lazily loading OCR engine: {engine_name}")
            
            if engine_name == "paddleocr":
                self._engines[engine_name] = PaddleOCRService(
                    languages=settings.OCR_LANGUAGES,
                    use_gpu=settings.OCR_GPU
                )
            elif engine_name == "easyocr":
                self._engines[engine_name] = EasyOCRService(
                    languages=settings.OCR_LANGUAGES,
                    use_gpu=settings.OCR_GPU
                )
        
        return self._engines[engine_name]
    
    def recognize(self, image, engine_name: str, mode: str = "printed") -> Dict:
        """
        Распознать текст с помощью указанного движка
        
        Args:
            image: Изображение (numpy array)
            engine_name: "paddleocr" или "easyocr"
            mode: "printed" или "handwritten"
            
        Returns:
            Результаты распознавания
        """
        engine = self._get_engine(engine_name)
        
        if mode == "handwritten":
            return engine.recognize_handwritten(image)
        else:
            return engine.recognize_printed(image)


# Глобальный экземпляр менеджера
_ocr_manager_instance: Optional[OCRManager] = None


def get_ocr_manager() -> OCRManager:
    """Получить OCR менеджер (singleton)"""
    global _ocr_manager_instance
    if _ocr_manager_instance is None:
        _ocr_manager_instance = OCRManager()
    return _ocr_manager_instance
