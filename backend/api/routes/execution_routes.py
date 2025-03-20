# backend/api/routes/execution_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...services.execution.execution_service import ExecutionService
from ...db.repositories.flow_repository import FlowRepository
from ...db.repositories.execution_repository import ExecutionRepository
from ..models.execution_models import (
    ExecutionRequest,
    ExecutionResponse,
    ExecutionDetailsResponse
)

router = APIRouter(prefix="/executions", tags=["executions"])

def get_execution_service(db: Session = Depends(get_db)):
    flow_repo = FlowRepository(db)
    execution_repo = ExecutionRepository(db)
    return ExecutionService(flow_repo, execution_repo)

@router.post("/", response_model=ExecutionResponse)
async def execute_flow(
    request: ExecutionRequest,
    execution_service: ExecutionService = Depends(get_execution_service)
):
    try:
        result = await execution_service.execute_flow(
            flow_id=request.flow_id,
            input_data=request.input,
            framework=request.framework
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{execution_id}", response_model=ExecutionDetailsResponse)
async def get_execution(
    execution_id: str,
    db: Session = Depends(get_db)
):
    execution_repo = ExecutionRepository(db)
    execution = execution_repo.get_by_id(execution_id)
    
    if not execution:
        raise HTTPException(status_code=404, detail=f"Execution with ID {execution_id} not found")
    
    return execution
