# init_project.py
"""
Скрипт для автоматической инициализации структуры OCR Desktop проекта
"""
import os
from pathlib import Path

def create_directory_structure():
    """Создание всей структуры папок проекта"""
    
    # Базовая структура
    directories = [
        # App core
        "python-backend/app",
        "python-backend/app/core",
        "python-backend/app/api",
        "python-backend/app/api/v1",
        "python-backend/app/api/v1/endpoints",
        
        # Models & Schemas
        "python-backend/app/models",
        "python-backend/app/schemas",
        
        # Services
        "python-backend/app/services",
        "python-backend/app/services/ocr",
        "python-backend/app/services/sync",
        
        # Database
        "python-backend/app/db",
        
        # Utils & Workers
        "python-backend/app/utils",
        "python-backend/app/workers",
        
        # Tests
        "python-backend/tests",
        "python-backend/tests/unit",
        "python-backend/tests/integration",
        
        # Migrations
        "python-backend/migrations",
        "python-backend/migrations/versions",
        
        # Storage (для разработки)
        "python-backend/storage",
        "python-backend/storage/watch",
        "python-backend/storage/processed",
        "python-backend/storage/database",
        "python-backend/storage/cache",
        
        # Logs
        "python-backend/logs",
    ]
    
    print("Создание структуры папок...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"{directory}")
    
    # Создание __init__.py файлов
    init_files = [
        "python-backend/app/__init__.py",
        "python-backend/app/core/__init__.py",
        "python-backend/app/api/__init__.py",
        "python-backend/app/api/v1/__init__.py",
        "python-backend/app/api/v1/endpoints/__init__.py",
        "python-backend/app/models/__init__.py",
        "python-backend/app/schemas/__init__.py",
        "python-backend/app/services/__init__.py",
        "python-backend/app/services/ocr/__init__.py",
        "python-backend/app/services/sync/__init__.py",
        "python-backend/app/db/__init__.py",
        "python-backend/app/utils/__init__.py",
        "python-backend/app/workers/__init__.py",
        "python-backend/tests/__init__.py",
        "python-backend/tests/unit/__init__.py",
        "python-backend/tests/integration/__init__.py",
    ]
    
    print("\nСоздание __init__.py файлов...")
    for init_file in init_files:
        Path(init_file).touch()
        print(f"✓ {init_file}")
    
    print("\nСтруктура проекта создана успешно!")

if __name__ == "__main__":
    create_directory_structure()
