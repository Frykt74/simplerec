"""
PaddleOCR 3.x интеграция для распознавания текста
"""
from typing import Dict, List
import numpy as np
import logging
from pathlib import Path

from app.services.ocr.base import BaseOCR
from app.core.exceptions import OCRInitError, OCRProcessError
from app.core.config import settings

logger = logging.getLogger(__name__)


class PaddleOCRService(BaseOCR):
    """Сервис OCR на базе PaddleOCR"""
    
    def __init__(self, languages: List[str] = None, use_gpu: bool = False):
        """
        Инициализация PaddleOCR
        
        Args:
            languages: Языки распознавания (первый язык основной)
            use_gpu: Использовать GPU
        """
        try:
            from paddleocr import PaddleOCR
            
            langs = languages or settings.OCR_LANGUAGES
            lang = langs[0] if langs else "en"
            
            logger.info(f"Initializing PaddleOCR: lang={lang}, gpu={use_gpu}")
            
            self.ocr = PaddleOCR(
                lang=lang,
                use_gpu=use_gpu,
                use_angle_cls=True,  # Определение ориентации
                show_log=False,
                use_space_char=True,
            )
            
            self.languages = langs
            self.use_gpu = use_gpu
            
            logger.info("PaddleOCR initialized successfully")
            
        except ImportError as e:
            raise OCRInitError("paddleocr", f"PaddleOCR not installed: {e}")
        except Exception as e:
            raise OCRInitError("paddleocr", str(e))
    
    def recognize_printed(self, image: np.ndarray) -> Dict:
        """
        Распознать печатный текст
        
        Args:
            image: Изображение (RGB numpy array)
            
        Returns:
            {"text": str, "confidence": float, "lines": [...], "boxes": [...]}
        """
        try:
            results = self.ocr.ocr(image, cls=True)
            return self._format_results(results)
        
        except Exception as e:
            logger.error(f"PaddleOCR printed recognition failed: {e}")
            raise OCRProcessError("image", str(e))
    
    def recognize_handwritten(self, image: np.ndarray) -> Dict:
        """
        Распознать рукописный текст
        
        Для рукописного лучше использовать специальные модели,
        но базовая версия тоже даст результат
        """
        try:
            results = self.ocr.ocr(image, cls=True)
            return self._format_results(results)
        
        except Exception as e:
            logger.error(f"PaddleOCR handwritten recognition failed: {e}")
            raise OCRProcessError("image", str(e))
    
    def recognize_from_file(self, image_path: str) -> Dict:
        """Распознать текст из файла"""
        try:
            results = self.ocr.ocr(image_path, cls=True)
            return self._format_results(results)
        except Exception as e:
            raise OCRProcessError(image_path, str(e))
    
    def _format_results(self, results: List) -> Dict:
        """
        Форматировать результаты PaddleOCR в единый формат
        
        PaddleOCR 3.x возвращает: [[[bbox, (text, confidence)], ...]]
        """
        if not results or results[0] is None:
            return {
                "text": "",
                "confidence": 0.0,
                "lines": [],
                "boxes": []
            }
        
        all_text = []
        all_lines = []
        total_confidence = 0.0
        count = 0
        
        page_results = results[0]
        
        if page_results is None:
            return {"text": "", "confidence": 0.0, "lines": [], "boxes": []}
        
        for line in page_results:
            if len(line) >= 2:
                bbox = line[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                text_info = line[1]  # (text, confidence)
                
                if isinstance(text_info, tuple) and len(text_info) >= 2:
                    text = text_info[0]
                    confidence = float(text_info[1])
                    
                    all_text.append(text)
                    total_confidence += confidence
                    count += 1
                    
                    all_lines.append({
                        "text": text,
                        "confidence": confidence,
                        "bbox": bbox
                    })
        
        avg_confidence = total_confidence / count if count > 0 else 0.0
        
        return {
            "text": "\n".join(all_text),
            "confidence": avg_confidence,
            "lines": all_lines,
            "boxes": [line["bbox"] for line in all_lines]
        }


# Глобальный экземпляр (ленивая инициализация)
_ocr_instance = None


def get_paddleocr() -> PaddleOCRService:
    """Получить OCR сервис (singleton)"""
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = PaddleOCRService(
            languages=settings.OCR_LANGUAGES,
            use_gpu=settings.OCR_GPU
        )
    return _ocr_instance
