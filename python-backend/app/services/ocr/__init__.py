from app.services.ocr.base import BaseOCR
from app.services.ocr.paddleocr_service import PaddleOCRService
from app.services.ocr.easyocr_service import EasyOCRService
from app.services.ocr.ocr_manager import OCRManager, get_ocr_manager

__all__ = [
    "BaseOCR",
    "PaddleOCRService",
    "EasyOCRService",
    "OCRManager",
    "get_ocr_manager",
]
