# backend/db/repositories/deployment_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ..models.deployment_model import DeploymentModel

class DeploymentRepository:
    """Repository for Deployment entities"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, deployment_id: str) -> Optional[DeploymentModel]:
        """Get a deployment by ID"""
        return self.db.query(DeploymentModel).filter(DeploymentModel.id == deployment_id).first()
    
    def get_by_flow_id(self, flow_id: str) -> List[DeploymentModel]:
        """Get deployments for a flow"""
        return self.db.query(DeploymentModel).filter(DeploymentModel.flow_id == flow_id).all()
    
    def create(self, deployment_data: Dict[str, Any]) -> DeploymentModel:
        """Create a new deployment"""
        deployment = DeploymentModel(**deployment_data)
        self.db.add(deployment)
        self.db.commit()
        self.db.refresh(deployment)
        return deployment
    
    def update(self, deployment_id: str, deployment_data: Dict[str, Any]) -> Optional[DeploymentModel]:
        """Update a deployment"""
        deployment = self.get_by_id(deployment_id)
        if not deployment:
            return None
        
        for key, value in deployment_data.items():
            setattr(deployment, key, value)
            
        self.db.commit()
        self.db.refresh(deployment)
        return deployment
    
    def delete(self, deployment_id: str) -> bool:
        """Delete a deployment"""
        deployment = self.get_by_id(deployment_id)
        if not deployment:
            return False
        
        self.db.delete(deployment)
        self.db.commit()
        return True
    
    def get_active_deployments(self) -> List[DeploymentModel]:
        """Get all active deployments"""
        return self.db.query(DeploymentModel).filter(DeploymentModel.status == "active").all()

    def get_all(self) -> List[DeploymentModel]:
        """Get all deployments"""
        return self.db.query(DeploymentModel).all()
