# backend/api/handlers/execution_handler.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
import json
import asyncio

from ...db.session import get_db
from ...services.flow.flow_service import FlowService
from ...db.repositories.flow_repository import FlowRepository
from ...services.execution.execution_service import ExecutionService
from ...db.repositories.execution_repository import ExecutionRepository
from ..models.execution_models import (
    ExecutionRequest,
    ExecutionResponse,
    ExecutionDetailsResponse,
    ExecutionListResponse
)
from ..middleware.auth_middleware import verify_api_key

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/executions", tags=["executions"])

def get_execution_service(db: Session = Depends(get_db)):
    """Dependency to get the execution service"""
    flow_repo = FlowRepository(db)
    execution_repo = ExecutionRepository(db)
    flow_service = FlowService(flow_repo)
    return ExecutionService(flow_repo, execution_repo)

@router.post("/", response_model=ExecutionResponse)
async def execute_flow(
    request: ExecutionRequest,
    background_tasks: BackgroundTasks,
    execution_service: ExecutionService = Depends(get_execution_service),
    user_info: dict = Depends(verify_api_key)
):
    """Execute a flow with the provided input data
    
    This endpoint initiates flow execution and returns immediately with 
    an execution ID. The execution continues in the background.
    """
    try:
        result = await execution_service.execute_flow(
            flow_id=request.flow_id,
            input_data=request.input,
            framework=request.framework,
            streaming=True  # Run in background
        )
        
        return ExecutionResponse(
            execution_id=result.get("execution_id", "unknown"),
            status="started",
            result=None
        )
    except ValueError as e:
        logger.warning(f"Invalid execution request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error executing flow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{execution_id}", response_model=ExecutionDetailsResponse)
async def get_execution(
    execution_id: str,
    execution_service: ExecutionService = Depends(get_execution_service),
    user_info: dict = Depends(verify_api_key)
):
    """Get execution details by ID"""
    try:
        execution = await execution_service.get_execution_status(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail=f"Execution with ID {execution_id} not found")
        return execution
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error retrieving execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/flow/{flow_id}", response_model=ExecutionListResponse)
async def get_flow_executions(
    flow_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    execution_service: ExecutionService = Depends(get_execution_service),
    user_info: dict = Depends(verify_api_key)
):
    """Get executions for a specific flow"""
    try:
        executions = await execution_service.get_flow_executions(flow_id, skip, limit)
        
        return ExecutionListResponse(
            items=executions,
            total=len(executions)  # In a real implementation, this would be a count query
        )
    except Exception as e:
        logger.exception(f"Error retrieving flow executions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=ExecutionListResponse)
async def get_recent_executions(
    limit: int = Query(10, ge=1, le=50),
    execution_service: ExecutionService = Depends(get_execution_service),
    user_info: dict = Depends(verify_api_key)
):
    """Get recent executions across all flows"""
    try:
        executions = await execution_service.get_recent_executions(limit)
        
        return ExecutionListResponse(
            items=executions,
            total=len(executions)
        )
    except Exception as e:
        logger.exception(f"Error retrieving recent executions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=Dict[str, Any])
async def get_execution_stats(
    execution_service: ExecutionService = Depends(get_execution_service),
    user_info: dict = Depends(verify_api_key)
):
    """Get execution statistics"""
    try:
        return await execution_service.get_execution_stats()
    except Exception as e:
        logger.exception(f"Error retrieving execution stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{execution_id}")
async def delete_execution(
    execution_id: str,
    execution_service: ExecutionService = Depends(get_execution_service),
    user_info: dict = Depends(verify_api_key)
):
    """Delete an execution"""
    try:
        # Only allow deleting completed or failed executions
        execution = await execution_service.get_execution_status(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail=f"Execution with ID {execution_id} not found")
            
        if execution["status"] not in ["completed", "failed", "cancelled"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete execution in '{execution['status']}' state"
            )
            
        deleted = await execution_service.delete_execution(execution_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Execution with ID {execution_id} not found")
            
        return {"message": f"Execution {execution_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{execution_id}/cancel")
async def cancel_execution(
    execution_id: str,
    execution_service: ExecutionService = Depends(get_execution_service),
    user_info: dict = Depends(verify_api_key)
):
    """Cancel an ongoing execution"""
    try:
        cancelled = await execution_service.cancel_execution(execution_id)
        if not cancelled:
            raise HTTPException(
                status_code=400, 
                detail=f"Execution {execution_id} could not be cancelled or does not exist"
            )
            
        return {"message": f"Execution {execution_id} cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error cancelling execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time execution updates
@router.websocket("/ws/{execution_id}")
async def execution_websocket(
    websocket: WebSocket, 
    execution_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time execution updates"""
    await websocket.accept()
    
    try:
        # Initialize execution service
        flow_repo = FlowRepository(db)
        execution_repo = ExecutionRepository(db)
        execution_service = ExecutionService(flow_repo, execution_repo)
        
        # Verify execution exists
        execution = await execution_service.get_execution_status(execution_id)
        if not execution:
            await websocket.close(code=1008, reason=f"Execution {execution_id} not found")
            return
            
        # Track last step seen to send only new updates
        last_step_seen = 0
        
        # Keep connection open and send updates
        while True:
            # Get latest execution status
            current_execution = await execution_service.get_execution_status(execution_id)
            
            # Check if execution is complete or failed
            if current_execution["status"] in ["completed", "failed", "cancelled"]:
                # Send final update
                await websocket.send_json({
                    "execution_id": execution_id,
                    "status": current_execution["status"],
                    "result": current_execution.get("result"),
                    "error": current_execution.get("error"),
                    "complete": True
                })
                
                # Close connection after sending final update
                await websocket.close()
                break
            
            # Send any new steps in the execution trace
            execution_trace = current_execution.get("execution_trace", [])
            new_steps = [
                step for step in execution_trace 
                if step.get("step", 0) > last_step_seen
            ]
            
            if new_steps:
                # Update last step seen
                last_step_seen = max(step.get("step", 0) for step in new_steps)
                
                # Send update
                await websocket.send_json({
                    "execution_id": execution_id,
                    "status": current_execution["status"],
                    "new_steps": new_steps,
                    "complete": False
                })
            
            # Wait before checking again
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket connection closed for execution {execution_id}")
    except Exception as e:
        logger.exception(f"Error in execution WebSocket: {str(e)}")
        await websocket.close(code=1011, reason=f"Internal server error: {str(e)}")
