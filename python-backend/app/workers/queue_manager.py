import asyncio
import logging
from dataclasses import dataclass, field
from typing import Callable, Any

logger = logging.getLogger(__name__)


@dataclass(order=True)
class Task:
    """Задача для выполнения в очереди"""
    priority: int
    data: Any = field(compare=False)


class QueueManager:
    """Асинхронная очередь задач для обработки OCR"""
    
    def __init__(self, worker_func: Callable, num_workers: int = 1):
        self.queue = asyncio.PriorityQueue()
        self.worker_func = worker_func
        self.num_workers = num_workers
        self._tasks = []
    
    async def add_task(self, data: Any, priority: int = 10):
        """Добавить задачу в очередь"""
        task = Task(priority=priority, data=data)
        await self.queue.put(task)
        logger.info(f"Task added to queue: {data}")
    
    async def _worker(self, name: str):
        """Воркер, который берет задачи из очереди и выполняет их"""
        logger.info(f"Worker '{name}' started")
        while True:
            try:
                task = await self.queue.get()
                logger.info(f"Worker '{name}' processing task: {task.data}")
                await self.worker_func(task.data)
                self.queue.task_done()
                logger.info(f"Worker '{name}' finished task: {task.data}")
            except asyncio.CancelledError:
                logger.info(f"Worker '{name}' stopping.")
                break
            except Exception as e:
                logger.exception(f"Worker '{name}' error processing {task.data}: {e}")
    
    async def start(self):
        """Запустить воркеров"""
        self._tasks = [
            asyncio.create_task(self._worker(f"OCR-Worker-{i+1}"))
            for i in range(self.num_workers)
        ]
        logger.info(f"{self.num_workers} workers started.")
    
    async def stop(self):
        """Остановить воркеров"""
        logger.info("Stopping workers...")
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        logger.info("All workers stopped.")
        