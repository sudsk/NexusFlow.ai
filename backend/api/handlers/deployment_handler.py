# backend/api/handlers/deployment_handler.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
import secrets

from ...db.session import get_db
from ...services.deployment.deployment_service import DeploymentService
from ...db.repositories.flow_repository import FlowRepository
from ...db.repositories.deployment_repository import DeploymentRepository
from ...services.execution.execution_service import ExecutionService
from ...db.repositories.execution_repository import ExecutionRepository
from ..models.deployment_models import (
    DeploymentCreateRequest,
    DeploymentUpdateRequest,
    DeploymentResponse,
    DeploymentListResponse
)
from ..models.execution_models import (
    ExecutionRequest,
    ExecutionResponse
)
from ..middleware.auth_middleware import verify_api_key, get_admin_user

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/deployments", tags=["deployments"])

def get_deployment_service(db: Session = Depends(get_db)):
    """Dependency to get the deployment service"""
    flow_repo = FlowRepository(db)
    deployment_repo = DeploymentRepository(db)
    return DeploymentService(flow_repo, deployment_repo)

def get_execution_service(db: Session = Depends(get_db)):
    """Dependency to get the execution service"""
    flow_repo = FlowRepository(db)
    execution_repo = ExecutionRepository(db)
    return ExecutionService(flow_repo, execution_repo)

@router.post("/{flow_id}", response_model=DeploymentResponse)
async def deploy_flow(
    flow_id: str,
    request: DeploymentCreateRequest,
    deployment_service: DeploymentService = Depends(get_deployment_service),
    user_info: dict = Depends(verify_api_key)  # Require authentication
):
    """Deploy a flow for API access
    
    This creates a new deployment for the specified flow,
    making it accessible via an API endpoint.
    """
    try:
        # Convert request to dictionary
        deployment_data = request.dict(exclude_unset=True)
        
        # Set default values if not provided
        if not deployment_data.get("name"):
            deployment_data["name"] = f"Deployment-{secrets.token_hex(4)}"
            
        if not deployment_data.get("settings"):
            deployment_data["settings"] = {
                "max_concurrent_executions": 5,
                "timeout_seconds": 300,
                "enable_caching": False
            }
        
        # Create deployment
        deployment = await deployment_service.deploy_flow(flow_id, deployment_data)
        return deployment
    except ValueError as e:
        logger.warning(f"Invalid deployment request: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Error deploying flow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: str,
    deployment_service: DeploymentService = Depends(get_deployment_service),
    user_info: dict = Depends(verify_api_key)  # Require authentication
):
    """Get a deployment by ID"""
    deployment = await deployment_service.get_deployment(deployment_id)
    
    if not deployment:
        raise HTTPException(status_code=404, detail=f"Deployment with ID {deployment_id} not found")
    
    return deployment

@router.get("/flow/{flow_id}", response_model=DeploymentListResponse)
async def get_flow_deployments(
    flow_id: str,
    deployment_service: DeploymentService = Depends(get_deployment_service),
    user_info: dict = Depends(verify_api_key)  # Require authentication
):
    """Get deployments for a flow"""
    deployments = await deployment_service.get_flow_deployments(flow_id)
    
    return DeploymentListResponse(
        items=deployments,
        total=len(deployments)
    )

@router.put("/{deployment_id}", response_model=DeploymentResponse)
async def update_deployment(
    deployment_id: str,
    request: DeploymentUpdateRequest,
    deployment_service: DeploymentService = Depends(get_deployment_service),
    user_info: dict = Depends(verify_api_key)  # Require authentication
):
    """Update a deployment"""
    # Extract only the values that are not None
    updated_data = {k: v for k, v in request.dict().items() if v is not None}
    
    deployment = await deployment_service.update_deployment(deployment_id, updated_data)
    
    if not deployment:
        raise HTTPException(status_code=404, detail=f"Deployment with ID {deployment_id} not found")
    
    return deployment

@router.delete("/{deployment_id}")
async def delete_deployment(
    deployment_id: str,
    deployment_service: DeploymentService = Depends(get_deployment_service),
    user_info: dict = Depends(verify_api_key)  # Require authentication
):
    """Delete a deployment"""
    success = await deployment_service.delete_deployment(deployment_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Deployment with ID {deployment_id} not found")
    
    return {"message": f"Deployment with ID {deployment_id} successfully deleted"}

@router.post("/{deployment_id}/deactivate")
async def deactivate_deployment(
    deployment_id: str,
    deployment_service: DeploymentService = Depends(get_deployment_service),
    user_info: dict = Depends(verify_api_key)  # Require authentication
):
    """Deactivate a deployment"""
    success = await deployment_service.deactivate_deployment(deployment_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Deployment with ID {deployment_id} not found")
    
    return {"message": f"Deployment with ID {deployment_id} successfully deactivated"}

@router.post("/{deployment_id}/execute", response_model=ExecutionResponse)
async def execute_deployment(
    deployment_id: str,
    request: ExecutionRequest,
    background_tasks: BackgroundTasks,
    deployment_service: DeploymentService = Depends(get_deployment_service),
    execution_service: ExecutionService = Depends(get_execution_service),
    user_info: dict = Depends(verify_api_key)  # Require authentication
):
    """Execute a deployment
    
    This executes a deployed flow with the provided input.
    """
    try:
        # Get deployment
        deployment = await deployment_service.get_deployment(deployment_id)
        
        if not deployment:
            raise HTTPException(status_code=404, detail=f"Deployment with ID {deployment_id} not found")
            
        # Check if deployment is active
        if deployment["status"] != "active":
            raise HTTPException(status_code=400, detail=f"Deployment with ID {deployment_id} is not active")
            
        # Get flow ID from deployment
        flow_id = deployment["flow_id"]
        
        # Execute flow
        result = await execution_service.execute_flow(
            flow_id=flow_id,
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
        logger.exception(f"Error executing deployment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
