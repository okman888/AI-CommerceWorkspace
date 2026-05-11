"""Workflows API endpoints."""
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.swarm.base import AgentStatus
from app.services.swarm.orchestrator import get_orchestrator

router = APIRouter()


class WorkflowStepCreate(BaseModel):
    """Workflow step creation request."""
    agent_id: str
    task: dict[str, Any]
    dependencies: list[str] = []


class WorkflowCreate(BaseModel):
    """Workflow creation request."""
    name: str
    steps: list[WorkflowStepCreate]


class WorkflowStepResponse(BaseModel):
    """Workflow step response."""
    step_id: str
    agent_id: str
    task: dict[str, Any]
    status: AgentStatus


class WorkflowResponse(BaseModel):
    """Workflow response."""
    workflow_id: str
    name: str
    steps: list[WorkflowStepResponse]
    status: AgentStatus


class WorkflowExecuteResponse(BaseModel):
    """Workflow execution response."""
    workflow_id: str
    status: AgentStatus
    message: str


@router.get("/", response_model=list[WorkflowResponse])
async def list_workflows() -> list[WorkflowResponse]:
    """List all workflows."""
    orchestrator = get_orchestrator()
    workflows = []
    for wf in orchestrator.workflows.values():
        workflows.append(
            WorkflowResponse(
                workflow_id=str(wf.workflow_id),
                name=wf.name,
                steps=[
                    WorkflowStepResponse(
                        step_id=str(step.step_id),
                        agent_id=step.agent_id,
                        task=step.task,
                        status=step.status,
                    )
                    for step in wf.steps
                ],
                status=wf.status,
            )
        )
    return workflows


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str) -> WorkflowResponse:
    """Get a specific workflow by ID."""
    from uuid import UUID
    orchestrator = get_orchestrator()
    try:
        wf = orchestrator.get_workflow(UUID(workflow_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workflow ID format")
    
    if not wf:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
    
    return WorkflowResponse(
        workflow_id=str(wf.workflow_id),
        name=wf.name,
        steps=[
            WorkflowStepResponse(
                step_id=str(step.step_id),
                agent_id=step.agent_id,
                task=step.task,
                status=step.status,
            )
            for step in wf.steps
        ],
        status=wf.status,
    )


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(request: WorkflowCreate) -> WorkflowResponse:
    """Create a new workflow."""
    orchestrator = get_orchestrator()
    
    steps_data = [
        {
            "agent_id": step.agent_id,
            "task": step.task,
            "dependencies": step.dependencies,
        }
        for step in request.steps
    ]
    
    wf = await orchestrator.create_workflow(name=request.name, steps=steps_data)
    
    return WorkflowResponse(
        workflow_id=str(wf.workflow_id),
        name=wf.name,
        steps=[
            WorkflowStepResponse(
                step_id=str(step.step_id),
                agent_id=step.agent_id,
                task=step.task,
                status=step.status,
            )
            for step in wf.steps
        ],
        status=wf.status,
    )


@router.post("/{workflow_id}/execute", response_model=WorkflowExecuteResponse)
async def execute_workflow(workflow_id: str) -> WorkflowExecuteResponse:
    """Execute a workflow."""
    from uuid import UUID
    orchestrator = get_orchestrator()
    
    try:
        wf = await orchestrator.execute_workflow(UUID(workflow_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workflow ID format")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return WorkflowExecuteResponse(
        workflow_id=str(wf.workflow_id),
        status=wf.status,
        message="Workflow executed successfully" if wf.status == AgentStatus.COMPLETED else "Workflow execution failed",
    )
