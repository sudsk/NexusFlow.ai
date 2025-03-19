# backend/api/routes/flow_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...core.entities.flow import Flow
from ...services.flow.flow_service import FlowService
from ...adapters.registry import get_adapter_registry
from ..models.flow_models import (
    FlowCreateRequest, 
    FlowUpdateRequest, 
    FlowResponse,
    FlowExecutionRequest, 
    FlowExecutionResponse
)

router = APIRouter(prefix="/flows", tags=["flows"])

def get_flow_service(db: Session = Depends(get_db)):
    adapter_registry = get_adapter_registry()
    return FlowService(FlowRepository(db), adapter_registry)

@router.post("/", response_model=FlowResponse, status_code=status.HTTP_201_CREATED)
async def create_flow(request: FlowCreateRequest, flow_service: FlowService = Depends(get_flow_service)):
    flow = await flow_service.create_flow(request.dict())
    return FlowResponse(**flow.to_dict())

@router.get("/{flow_id}", response_model=FlowResponse)
async def get_flow(flow_id: str, flow_service: FlowService = Depends(get_flow_service)):
    flow = await flow_service.get_flow(flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail=f"Flow with ID {flow_id} not found")
    return FlowResponse(**flow.to_dict())

@router.put("/{flow_id}", response_model=FlowResponse)
async def update_flow(flow_id: str, request: FlowUpdateRequest, flow_service: FlowService = Depends(get_flow_service)):
    flow = await flow_service.update_flow(flow_id, request.dict())
    if not flow:
        raise HTTPException(status_code=404, detail=f"Flow with ID {flow_id} not found")
    return FlowResponse(**flow.to_dict())

@router.delete("/{flow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flow(flow_id: str, flow_service: FlowService = Depends(get_flow_service)):
    success = await flow_service.delete_flow(flow_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Flow with ID {flow_id} not found")
    return None

@router.get("/", response_model=List[FlowResponse])
async def list_flows(
    skip: int = 0, 
    limit: int = 100, 
    name: str = None,
    flow_service: FlowService = Depends(get_flow_service)
):
    flows = await flow_service.list_flows(skip, limit, name)
    return [FlowResponse(**flow.to_dict()) for flow in flows]

@router.post("/{flow_id}/execute", response_model=FlowExecutionResponse)
async def execute_flow(
    flow_id: str, 
    request: FlowExecutionRequest,
    flow_service: FlowService = Depends(get_flow_service)
):
    try:
        result = await flow_service.execute_flow(
            flow_id=flow_id,
            input_data=request.input,
            framework=request.framework
        )
        return FlowExecutionResponse(
            execution_id=result.get("execution_id", "unknown"),
            status="completed",
            result=result,
            error=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
