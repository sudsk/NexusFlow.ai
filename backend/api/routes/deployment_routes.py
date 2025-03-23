# backend/api/routes/deployment_routes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...services.deployment.deployment_service import DeploymentService
from ...db.repositories.flow_repository import FlowRepository
from ...db.repositories.deployment_repository import DeploymentRepository
from ..models.deployment_models import (
    DeploymentCreateRequest,
    DeploymentUpdateRequest,
    DeploymentResponse,
    DeploymentListResponse
)

router = APIRouter(prefix="/deployments", tags=["deployments"])

def get_deployment_service(db: Session = Depends(get_db)):
    flow_repo = FlowRepository(db)
    deployment_repo = DeploymentRepository(db)
    return DeploymentService(flow_repo, deployment_repo)

@router.post("/{flow_id}", response_model=DeploymentResponse)
async def deploy_flow(
    flow_id: str,
    request: DeploymentCreateRequest,
    deployment_service: DeploymentService = Depends(get_deployment_service)
):
    """Deploy a flow"""
    try:
        deployment = await deployment_service.deploy_flow(flow_id, request.dict())
        return deployment
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: str,
    deployment_service: DeploymentService = Depends(get_deployment_service)
):
    """Get a deployment by ID"""
    deployment = await deployment_service.get_deployment(deployment_id)
    
    if not deployment:
        raise HTTPException(status_code=404, detail=f"Deployment with ID {deployment_id} not found")
    
    return deployment

@router.get("/flow/{flow_id}", response_model=DeploymentListResponse)
async def get_flow_deployments(
    flow_id: str,
    deployment_service: DeploymentService = Depends(get_deployment_service)
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
    deployment_service: DeploymentService = Depends(get_deployment_service)
):
    """Update a deployment"""
    updated_data = {k: v for k, v in request.dict().items() if v is not None}
    deployment = await deployment_service.update_deployment(deployment_id, updated_data)
    
    if not deployment:
        raise HTTPException(status_code=404, detail=f"Deployment with ID {deployment_id} not found")
    
    return deployment

@router.delete("/{deployment_id}")
async def delete_deployment(
    deployment_id: str,
    deployment_service: DeploymentService = Depends(get_deployment_service)
):
    """Delete a deployment"""
    success = await deployment_service.delete_deployment(deployment_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Deployment with ID {deployment_id} not found")
    
    return {"message": f"Deployment with ID {deployment_id} successfully deleted"}

@router.post("/{deployment_id}/deactivate")
async def deactivate_deployment(
    deployment_id: str,
    deployment_service: DeploymentService = Depends(get_deployment_service)
):
    """Deactivate a deployment"""
    success = await deployment_service.deactivate_deployment(deployment_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Deployment with ID {deployment_id} not found")
    
    return {"message": f"Deployment with ID {deployment_id} successfully deactivated"}

@router.get("", response_model=DeploymentListResponse)
async def get_all_deployments(
    deployment_service: DeploymentService = Depends(get_deployment_service)
):
    """Get all deployments"""
    deployments = await deployment_service.get_all_deployments()
    
    return DeploymentListResponse(
        items=deployments,
        total=len(deployments)
    )
