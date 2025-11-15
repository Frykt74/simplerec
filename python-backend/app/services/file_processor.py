"""
Обработка файлов (PDF, изображения)
"""
from pathlib import Path
from typing import List, Dict, Optional, Generator
import numpy as np
import fitz  # PyMuPDF
from PIL import Image

from app.core.exceptions import FileFormatError, FileProcessError


class FileProcessor:
    """Обработчик файлов для OCR"""
    
    @staticmethod
    def extract_pdf_text(pdf_path: str) -> str:
        """
        Извлечь встроенный текст из PDF (если есть)
        
        Args:
            pdf_path: Путь к PDF файлу
            
        Returns:
            Текст из PDF (разделитель страниц: \\f)
        """
        try:
            doc = fitz.open(pdf_path)
            text_parts = []
            
            for page in doc:
                page_text = page.get_text()
                text_parts.append(page_text)
            
            doc.close()
            return "\f".join(text_parts)
        
        except Exception as e:
            raise FileProcessError(pdf_path, f"Failed to extract text: {e}")
    
    @staticmethod
    def pdf_to_images(
        pdf_path: str,
        dpi: int = 300
    ) -> Generator[np.ndarray, None, None]:
        """
        Конвертировать страницы PDF в изображения
        
        Args:
            pdf_path: Путь к PDF
            dpi: Разрешение для рендеринга
            
        Yields:
            Изображения страниц как numpy arrays (RGB)
        """
        try:
            doc = fitz.open(pdf_path)
            
            for page in doc:
                # Рендеринг страницы с заданным DPI
                mat = fitz.Matrix(dpi / 72, dpi / 72)
                pix = page.get_pixmap(matrix=mat)
                
                # Конвертация в numpy array
                img_array = np.frombuffer(pix.samples, dtype=np.uint8)
                img_array = img_array.reshape(pix.height, pix.width, pix.n)
                
                # Конвертация в RGB если нужно
                if pix.n == 4:  # RGBA
                    img_array = img_array[:, :, :3]
                
                yield img_array
            
            doc.close()
        
        except Exception as e:
            raise FileProcessError(pdf_path, f"Failed to convert to images: {e}")
    
    @staticmethod
    def get_pdf_info(pdf_path: str) -> Dict:
        """
        Получить информацию о PDF
        
        Returns:
            Dict с метаданными (page_count, has_text и т.д.)
        """
        try:
            doc = fitz.open(pdf_path)
            
            page_count = len(doc)
            has_text = False
            
            # Проверяем первую страницу на наличие текста
            if page_count > 0:
                first_page_text = doc[0].get_text().strip()
                has_text = len(first_page_text) > 50
            
            info = {
                "page_count": page_count,
                "has_text": has_text,
                "metadata": doc.metadata,
            }
            
            doc.close()
            return info
        
        except Exception as e:
            raise FileProcessError(pdf_path, f"Failed to get PDF info: {e}")
    
    @staticmethod
    def validate_pdf(pdf_path: str) -> bool:
        """Проверить валидность PDF"""
        try:
            doc = fitz.open(pdf_path)
            is_valid = len(doc) > 0
            doc.close()
            return is_valid
        except:
            return False
    
    @staticmethod
    def load_image(image_path: str) -> np.ndarray:
        """
        Загрузить изображение
        
        Returns:
            Изображение как numpy array (RGB)
        """
        try:
            img = Image.open(image_path)
            
            # Конвертация в RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            return np.array(img)
        
        except Exception as e:
            raise FileProcessError(image_path, f"Failed to load image: {e}")

@staticmethod
def process_pdf_with_ocr(
    pdf_path: str,
    ocr_manager,
    engine: str,
    dpi: int = 300,
    mode: str = "printed"
) -> Dict:
    """Обработать PDF через OCR"""
    
    all_text = []
    pages_info = []
    total_confidence = 0.0
    page_count = 0
    
    for idx, page_image in enumerate(FileProcessor.pdf_to_images(pdf_path, dpi), start=1):
        # ИСПОЛЬЗУЕМ МЕНЕДЖЕР
        result = ocr_manager.recognize(
            image=page_image,
            engine_name=engine,
            mode=mode
        )
        
        all_text.append(result["text"])
        total_confidence += result["confidence"]
        page_count += 1
        
        pages_info.append({
            "page_number": idx,
            "text": result["text"],
            "confidence": result["confidence"],
            "boxes": result.get("boxes", [])
        })
    
    return {
        "text": "\f".join(all_text),
        "pages": pages_info,
        "confidence": total_confidence / page_count if page_count > 0 else 0.0,
        "page_count": page_count
    }
