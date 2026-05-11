"""Base classes for Hermes Swarm Engine agents."""
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


class Message(BaseModel):
    """Message passed between agents."""
    id: UUID = Field(default_factory=uuid4)
    sender: str
    receiver: Optional[str] = None
    content: dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    reply_to: Optional[UUID] = None


class AgentResult(BaseModel):
    """Result from an agent execution."""
    success: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    agent_id: str
    execution_time: float = 0.0


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, agent_id: str, name: str, description: str = ""):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self._message_queue: list[Message] = []

    @abstractmethod
    async def execute(self, task: dict[str, Any]) -> AgentResult:
        """Execute the agent's task."""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent."""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the agent."""
        pass

    async def receive_message(self, message: Message) -> None:
        """Receive a message from another agent."""
        self._message_queue.append(message)

    def clear_queue(self) -> None:
        """Clear the message queue."""
        self._message_queue.clear()

    def get_status(self) -> AgentStatus:
        """Get current agent status."""
        return self.status

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.agent_id}, name={self.name})>"
