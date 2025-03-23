# backend/api/routes/flow_routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...core.entities.flow import Flow
from ...services.flow.flow_service import FlowService
from ...adapters.registry import get_adapter_registry
from ...db.repositories.flow_repository import FlowRepository
from ..models.flow_models import (
    FlowCreateRequest, 
    FlowUpdateRequest, 
    FlowResponse,
    FlowListResponse,
    FlowExecutionRequest, 
    FlowExecutionResponse,
    FlowValidationResponse,
    FlowExportResponse
)

router = APIRouter(prefix="/flows", tags=["flows"])

def get_flow_service(db: Session = Depends(get_db)):
    """Dependency to get the flow service"""
    flow_repo = FlowRepository(db)
    return FlowService(flow_repo)

@router.post("", response_model=FlowResponse, status_code=status.HTTP_201_CREATED)
async def create_flow(
    request: FlowCreateRequest, 
    flow_service: FlowService = Depends(get_flow_service)
):
    """Create a new flow"""
    try:
        flow = await flow_service.create_flow(request.dict())
        return flow
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating flow: {str(e)}")

@router.get("", response_model=FlowListResponse)
async def list_flows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    name: Optional[str] = None,
    framework: Optional[str] = None,
    flow_service: FlowService = Depends(get_flow_service)
):
    """List flows with optional filtering"""
    try:
        flows = await flow_service.list_flows(
            skip=skip, 
            limit=limit, 
            name=name,
            framework=framework
        )
        
        # Count total flows (with the same filters but no pagination)
        total_flows = await flow_service.count_flows(
            name=name,
            framework=framework
        )        
        
        return FlowListResponse(
            items=flows,
            total=total_flows,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing flows: {str(e)}")

@router.get("/{flow_id}", response_model=FlowResponse)
async def get_flow(
    flow_id: str,
    flow_service: FlowService = Depends(get_flow_service)
):
    """Get a flow by ID"""
    try:
        flow = await flow_service.get_flow(flow_id)
        if not flow:
            raise HTTPException(
                status_code=404, 
                detail=f"Flow with ID {flow_id} not found"
            )
        return flow
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving flow: {str(e)}")

@router.put("/{flow_id}", response_model=FlowResponse)
async def update_flow(
    flow_id: str,
    request: FlowUpdateRequest,
    flow_service: FlowService = Depends(get_flow_service)
):
    """Update an existing flow"""
    try:
        # Get only the provided fields (not None)
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        flow = await flow_service.update_flow(flow_id, update_data)
        if not flow:
            raise HTTPException(
                status_code=404, 
                detail=f"Flow with ID {flow_id} not found"
            )
        return flow
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating flow: {str(e)}")

@router.delete("/{flow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flow(
    flow_id: str,
    flow_service: FlowService = Depends(get_flow_service)
):
    """Delete a flow"""
    try:
        success = await flow_service.delete_flow(flow_id)
        if not success:
            raise HTTPException(
                status_code=404, 
                detail=f"Flow with ID {flow_id} not found"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting flow: {str(e)}")

@router.post("/{flow_id}/execute", response_model=FlowExecutionResponse)
async def execute_flow(
    flow_id: str,
    request: FlowExecutionRequest,
    flow_service: FlowService = Depends(get_flow_service)
):
    """Execute a flow"""
    try:
        # Check if flow exists
        flow = await flow_service.get_flow(flow_id)
        if not flow:
            raise HTTPException(
                status_code=404, 
                detail=f"Flow with ID {flow_id} not found"
            )
        
        # Execute the flow
        result = await flow_service.execute_flow(
            flow_id=flow_id,
            input_data=request.input,
            framework=request.framework
        )
        
        return FlowExecutionResponse(
            execution_id=result.get("execution_id", "unknown"),
            status="started",
            result=result,
            error=None
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error executing flow: {str(e)}"
        )

@router.post("/validate", response_model=FlowValidationResponse)
async def validate_flow(
    request: FlowCreateRequest,
    flow_service: FlowService = Depends(get_flow_service)
):
    """Validate a flow configuration"""
    try:
        validation_results = await flow_service.validate_flow(request.dict())
        return FlowValidationResponse(**validation_results)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error validating flow: {str(e)}"
        )

@router.get("/{flow_id}/export", response_model=FlowExportResponse)
async def export_flow(
    flow_id: str,
    target_framework: Optional[str] = None,
    flow_service: FlowService = Depends(get_flow_service)
):
    """Export a flow to a specific framework format"""
    try:
        export_result = await flow_service.export_flow(
            flow_id=flow_id,
            target_framework=target_framework
        )
        return FlowExportResponse(**export_result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error exporting flow: {str(e)}"
        )

@router.get("/{flow_id}/versions", response_model=List[FlowResponse])
async def get_flow_versions(
    flow_id: str,
    flow_service: FlowService = Depends(get_flow_service)
):
    """Get version history for a flow"""
    try:
        versions = await flow_service.get_flow_versions(flow_id)
        if not versions:
            raise HTTPException(
                status_code=404, 
                detail=f"Flow with ID {flow_id} not found or has no version history"
            )
        return versions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving flow versions: {str(e)}"
        )
