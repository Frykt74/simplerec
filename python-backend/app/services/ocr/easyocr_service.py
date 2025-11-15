"""
Реализация OCR-сервиса на базе EasyOCR
"""
from typing import Dict, List
import numpy as np
import logging

from app.services.ocr.base import BaseOCR
from app.core.exceptions import OCRInitError, OCRProcessError

logger = logging.getLogger(__name__)


class EasyOCRService(BaseOCR):
    """Сервис OCR с использованием EasyOCR"""
    
    def __init__(self, languages: List[str] = ['en', 'ru'], use_gpu: bool = False):
        """
        Инициализация EasyOCR
        
        Args:
            languages: Языки для распознавания
            use_gpu: Использовать GPU
        """
        try:
            import easyocr
            
            logger.info(f"Initializing EasyOCR: languages={languages}, gpu={use_gpu}")
            self.reader = easyocr.Reader(languages, gpu=use_gpu)
            logger.info("EasyOCR initialized successfully")
            
        except ImportError as e:
            raise OCRInitError("easyocr", f"EasyOCR not installed: {e}")
        except Exception as e:
            raise OCRInitError("easyocr", str(e))
    
    def recognize_printed(self, image: np.ndarray) -> Dict:
        """Распознать печатный текст"""
        return self._recognize(image)
    
    def recognize_handwritten(self, image: np.ndarray) -> Dict:
        """Распознать рукописный текст"""
        return self._recognize(image)
    
    def _recognize(self, image: np.ndarray) -> Dict:
        """Основная функция распознавания"""
        try:
            results = self.reader.readtext(image)
            return self._format_results(results)
        
        except Exception as e:
            logger.error(f"EasyOCR recognition failed: {e}")
            raise OCRProcessError("image", str(e))
    
    def _format_results(self, results: List) -> Dict:
        """
        Форматировать результаты EasyOCR в единый формат
        
        EasyOCR возвращает: [(bbox, text, confidence), ...]
        """
        if not results:
            return {"text": "", "confidence": 0.0, "lines": [], "boxes": []}
        
        all_text = []
        all_lines = []
        total_confidence = 0.0
        
        for bbox, text, confidence in results:
            all_text.append(text)
            total_confidence += confidence
            
            all_lines.append({
                "text": text,
                "confidence": float(confidence),
                "bbox": bbox
            })
        
        avg_confidence = total_confidence / len(results) if results else 0.0
        
        return {
            "text": "\n".join(all_text),
            "confidence": avg_confidence,
            "lines": all_lines,
            "boxes": [line["bbox"] for line in all_lines]
        }
    