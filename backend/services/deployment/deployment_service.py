# backend/services/deployment/deployment_service.py
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import secrets
import logging
from ...db.repositories.flow_repository import FlowRepository
from ...db.repositories.deployment_repository import DeploymentRepository

logger = logging.getLogger(__name__)

class DeploymentService:
    """Service for managing flow deployments"""
    
    def __init__(self, flow_repository: FlowRepository, deployment_repository: DeploymentRepository):
        self.flow_repository = flow_repository
        self.deployment_repository = deployment_repository
    
    async def deploy_flow(self, flow_id: str, deployment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy a flow
        
        Args:
            flow_id: ID of the flow to deploy
            deployment_data: Deployment configuration
            
        Returns:
            Deployment details
        """
        # Check if flow exists
        flow = self.flow_repository.get_by_id(flow_id)
        if not flow:
            raise ValueError(f"Flow with ID {flow_id} not found")
        
        # Generate API key
        api_key = secrets.token_hex(16)
        
        # Create deployment record
        deployment_id = str(uuid.uuid4())
        endpoint_path = f"/api/flows/{deployment_id}/execute"
        
        # Base URL - in production, this would be configurable
        base_url = "https://api.nexusflow.ai"  # Example
        
        deployment = {
            "id": deployment_id,
            "flow_id": flow_id,
            "name": deployment_data.get("name", flow.name),
            "version": deployment_data.get("version", "v1"),
            "status": "active",
            "api_key": api_key,
            "endpoint_url": f"{base_url}{endpoint_path}",
            "settings": deployment_data.get("settings", {})
        }
        
        # Save to database
        created_deployment = self.deployment_repository.create(deployment)
        
        return self._convert_to_dict(created_deployment)
    
    async def get_deployment(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get deployment details
        
        Args:
            deployment_id: ID of the deployment
            
        Returns:
            Deployment details or None if not found
        """
        deployment = self.deployment_repository.get_by_id(deployment_id)
        if not deployment:
            return None
            
        return self._convert_to_dict(deployment)
    
    async def get_flow_deployments(self, flow_id: str) -> List[Dict[str, Any]]:
        """
        Get deployments for a flow
        
        Args:
            flow_id: ID of the flow
            
        Returns:
            List of deployment dictionaries
        """
        deployments = self.deployment_repository.get_by_flow_id(flow_id)
        return [self._convert_to_dict(deployment) for deployment in deployments]
    
    async def update_deployment(self, deployment_id: str, deployment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a deployment
        
        Args:
            deployment_id: ID of the deployment
            deployment_data: Updated deployment data
            
        Returns:
            Updated deployment or None if not found
        """
        deployment = self.deployment_repository.update(deployment_id, deployment_data)
        return self._convert_to_dict(deployment) if deployment else None
    
    async def deactivate_deployment(self, deployment_id: str) -> bool:
        """
        Deactivate a deployment
        
        Args:
            deployment_id: ID of the deployment
            
        Returns:
            True if successful, False if not found
        """
        deployment = self.deployment_repository.get_by_id(deployment_id)
        if not deployment:
            return False
            
        return self.deployment_repository.update(deployment_id, {"status": "inactive"}) is not None
    
    async def delete_deployment(self, deployment_id: str) -> bool:
        """
        Delete a deployment
        
        Args:
            deployment_id: ID of the deployment
            
        Returns:
            True if deleted, False if not found
        """
        return self.deployment_repository.delete(deployment_id)
    
    def _convert_to_dict(self, deployment) -> Dict[str, Any]:
        """Convert deployment model to dictionary"""
        return {
            "id": deployment.id,
            "flow_id": deployment.flow_id,
            "name": deployment.name,
            "version": deployment.version,
            "status": deployment.status,
            "endpoint_url": deployment.endpoint_url,
            "created_at": deployment.created_at.isoformat() if deployment.created_at else None,
            "updated_at": deployment.updated_at.isoformat() if deployment.updated_at else None,
            "settings": deployment.settings or {}
        }
