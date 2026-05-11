"""Agents API endpoints."""
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.swarm.base import AgentStatus
from app.services.swarm.orchestrator import get_orchestrator

router = APIRouter()


class AgentCreate(BaseModel):
    """Agent creation request."""
    agent_id: str
    name: str
    description: str = ""


class AgentResponse(BaseModel):
    """Agent response."""
    agent_id: str
    name: str
    description: str
    status: AgentStatus


class AgentListResponse(BaseModel):
    """List of agents response."""
    agents: list[AgentResponse]
    total: int


@router.get("/", response_model=AgentListResponse)
async def list_agents() -> AgentListResponse:
    """List all registered agents."""
    orchestrator = get_orchestrator()
    agents = [
        AgentResponse(
            agent_id=agent.agent_id,
            name=agent.name,
            description=agent.description,
            status=agent.status,
        )
        for agent in orchestrator.agents.values()
    ]
    return AgentListResponse(agents=agents, total=len(agents))


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str) -> AgentResponse:
    """Get a specific agent by ID."""
    orchestrator = get_orchestrator()
    agent = orchestrator.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return AgentResponse(
        agent_id=agent.agent_id,
        name=agent.name,
        description=agent.description,
        status=agent.status,
    )


@router.post("/", response_model=AgentResponse)
async def register_agent(request: AgentCreate) -> AgentResponse:
    """Register a new agent."""
    from app.services.swarm.base import BaseAgent
    
    orchestrator = get_orchestrator()
    
    # Create a simple placeholder agent for now
    class PlaceholderAgent(BaseAgent):
        async def execute(self, task: dict[str, Any]) -> Any:
            return {"status": "completed"}
        async def initialize(self) -> None:
            pass
        async def shutdown(self) -> None:
            pass
    
    agent = PlaceholderAgent(agent_id=request.agent_id, name=request.name, description=request.description)
    orchestrator.register_agent(agent)
    
    return AgentResponse(
        agent_id=agent.agent_id,
        name=agent.name,
        description=agent.description,
        status=agent.status,
    )


@router.delete("/{agent_id}")
async def unregister_agent(agent_id: str) -> dict[str, str]:
    """Unregister an agent."""
    orchestrator = get_orchestrator()
    agent = orchestrator.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    orchestrator.unregister_agent(agent_id)
    return {"message": f"Agent {agent_id} unregistered"}
