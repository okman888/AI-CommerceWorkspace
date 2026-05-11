"""Worker abstraction for background task processing."""
from abc import ABC, abstractmethod
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.services.swarm.base import AgentResult, AgentStatus


class Task(BaseModel):
    """Task definition for workers."""
    id: UUID = Field(default_factory=uuid4)
    name: str
    payload: dict[str, Any]
    priority: int = 0
    retries: int = 0
    max_retries: int = 3
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[AgentResult] = None
    error: Optional[str] = None


class BaseWorker(ABC):
    """Abstract base class for workers."""

    def __init__(self, worker_id: str, name: str):
        self.worker_id = worker_id
        self.name = name
        self.is_running = False

    @abstractmethod
    async def process_task(self, task: Task) -> AgentResult:
        """Process a single task."""
        pass

    @abstractmethod
    async def start(self) -> None:
        """Start the worker."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the worker."""
        pass

    async def health_check(self) -> bool:
        """Check worker health."""
        return self.is_running

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.worker_id}, name={self.name})>"
