"""Orchestrator for managing multi-agent workflows."""
import asyncio
import logging
import time
from collections.abc import Callable
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.services.swarm.base import AgentResult, AgentStatus, BaseAgent, Message

logger = logging.getLogger(__name__)


class WorkflowStep(BaseModel):
    """A single step in a workflow."""
    step_id: UUID = Field(default_factory=uuid4)
    agent_id: str
    task: dict[str, Any]
    dependencies: list[UUID] = Field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[AgentResult] = None


class Workflow(BaseModel):
    """Workflow definition."""
    workflow_id: UUID = Field(default_factory=uuid4)
    name: str
    steps: list[WorkflowStep] = Field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    completed_at: Optional[datetime] = None


class Orchestrator:
    """Orchestrates multi-agent workflows."""

    def __init__(self):
        self.agents: dict[str, BaseAgent] = {}
        self.workflows: dict[UUID, Workflow] = {}
        self._running = False

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator."""
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent}")

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)

    async def create_workflow(self, name: str, steps: list[dict[str, Any]]) -> Workflow:
        """Create a new workflow."""
        workflow = Workflow(name=name)
        for step_data in steps:
            step = WorkflowStep(
                agent_id=step_data["agent_id"],
                task=step_data["task"],
                dependencies=[UUID(d) for d in step_data.get("dependencies", [])]
            )
            workflow.steps.append(step)
        self.workflows[workflow.workflow_id] = workflow
        return workflow

    async def execute_workflow(self, workflow_id: UUID) -> Workflow:
        """Execute a workflow."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow.status = AgentStatus.RUNNING
        start_time = time.time()

        try:
            for step in workflow.steps:
                # Wait for dependencies
                if step.dependencies:
                    await self._wait_for_dependencies(step)

                # Get the agent and execute
                agent = self.agents.get(step.agent_id)
                if not agent:
                    step.status = AgentStatus.FAILED
                    step.result = AgentResult(
                        success=False,
                        error=f"Agent {step.agent_id} not found",
                        agent_id=step.agent_id
                    )
                    continue

                step.status = AgentStatus.RUNNING
                agent.status = AgentStatus.RUNNING

                try:
                    result = await agent.execute(step.task)
                    step.result = result
                    step.status = AgentStatus.COMPLETED if result.success else AgentStatus.FAILED
                except Exception as e:
                    step.status = AgentStatus.FAILED
                    step.result = AgentResult(
                        success=False,
                        error=str(e),
                        agent_id=step.agent_id
                    )
                    logger.error(f"Step {step.step_id} failed: {e}")

            workflow.status = AgentStatus.COMPLETED
            workflow.completed_at = datetime.now()
        except Exception as e:
            workflow.status = AgentStatus.FAILED
            logger.error(f"Workflow {workflow_id} failed: {e}")

        return workflow

    async def _wait_for_dependencies(self, step: WorkflowStep) -> None:
        """Wait for dependency steps to complete."""
        workflow = None
        for wf in self.workflows.values():
            if step in wf.steps:
                workflow = wf
                break

        if not workflow:
            return

        for dep_id in step.dependencies:
            dep_step = next((s for s in workflow.steps if s.step_id == dep_id), None)
            while dep_step and dep_step.status not in [AgentStatus.COMPLETED, AgentStatus.FAILED]:
                await asyncio.sleep(0.1)

    async def send_message(self, message: Message) -> None:
        """Send a message to an agent."""
        if message.receiver:
            agent = self.agents.get(message.receiver)
            if agent:
                await agent.receive_message(message)
                logger.info(f"Message sent to {message.receiver} from {message.sender}")
        else:
            # Broadcast to all agents
            for agent in self.agents.values():
                await agent.receive_message(message)

    async def start(self) -> None:
        """Start the orchestrator."""
        self._running = True
        logger.info("Orchestrator started")

    async def stop(self) -> None:
        """Stop the orchestrator."""
        self._running = False
        for agent in self.agents.values():
            await agent.shutdown()
        logger.info("Orchestrator stopped")

    def get_workflow(self, workflow_id: UUID) -> Optional[Workflow]:
        """Get a workflow by ID."""
        return self.workflows.get(workflow_id)


# Global orchestrator instance
_orchestrator: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    """Get the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator
