"""
WebSocket endpoint для real-time уведомлений
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Менеджер WebSocket соединений"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Отправить сообщение всем подключенным клиентам"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")


manager = ConnectionManager()


@router.websocket("/updates")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket для получения обновлений в реальном времени
    
    События:
    - file_added: новый файл добавлен
    - processing_started: начата обработка
    - processing_completed: обработка завершена
    - processing_failed: ошибка обработки
    """
    await manager.connect(websocket)
    try:
        while True:
            # Держим соединение открытым
            data = await websocket.receive_text()
            # Можно обрабатывать команды от клиента
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def notify_file_added(file_id: int, filename: str):
    """Уведомить о новом файле"""
    await manager.broadcast({
        "type": "file_added",
        "file_id": file_id,
        "filename": filename
    })


async def notify_processing_started(file_id: int):
    """Уведомить о начале обработки"""
    await manager.broadcast({
        "type": "processing_started",
        "file_id": file_id
    })


async def notify_processing_completed(file_id: int, document_id: int):
    """Уведомить о завершении обработки"""
    await manager.broadcast({
        "type": "processing_completed",
        "file_id": file_id,
        "document_id": document_id
    })


async def notify_processing_failed(file_id: int, error: str):
    """Уведомить об ошибке"""
    await manager.broadcast({
        "type": "processing_failed",
        "file_id": file_id,
        "error": error
    })
    