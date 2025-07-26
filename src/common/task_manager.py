import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class TaskManager(ABC):
    @abstractmethod
    async def execute_task(self, body: dict):
        pass

class InMemoryTaskManager(TaskManager):
    async def execute_task(self, body: dict):
        logger.info(f"Received task: {body}")
        return {"status": "completed", "output": body}
