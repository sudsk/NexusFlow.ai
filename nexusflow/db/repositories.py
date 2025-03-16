from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import Flow, Execution, Deployment, Webhook

class FlowRepository:
    """Repository for Flow entities"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100, name: Optional[str] = None) -> List[Flow]:
        """Get all flows with optional filtering"""
        query = self.db.query(Flow)
        
        if name:
            query = query.filter(Flow.name.ilike(f"%{name}%"))
        
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, flow_id: str) -> Optional[Flow]:
        """Get a flow by ID"""
        return self.db.query(Flow).filter(Flow.id == flow_id).first()
    
    def create(self, flow_data: Dict[str, Any]) -> Flow:
        """Create a new flow"""
        flow = Flow(**flow_data)
        self.db.add(flow)
        self.db.commit()
        self.db.refresh(flow)
        return flow
    
    def update(self, flow_id: str, flow_data: Dict[str, Any]) -> Optional[Flow]:
        """Update an existing flow"""
        flow = self.get_by_id(flow_id)
        if not flow:
            return None
        
        # Update fields
        for key, value in flow_data.items():
            setattr(flow, key, value)
        
        flow.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(flow)
        return flow
    
    def delete(self, flow_id: str) -> bool:
        """Delete a flow"""
        flow = self.get_by_id(flow_id)
        if not flow:
            return False
        
        self.db.delete(flow)
        self.db.commit()
        return True


class ExecutionRepository:
    """Repository for Execution entities"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, execution_id: str) -> Optional[Execution]:
        """Get an execution by ID"""
        return self.db.query(Execution).filter(Execution.id == execution_id).first()
    
    def get_by_flow_id(self, flow_id: str, skip: int = 0, limit: int = 100) -> List[Execution]:
        """Get executions for a flow"""
        return self.db.query(Execution)\
            .filter(Execution.flow_id == flow_id)\
            .order_by(Execution.started_at.desc())\
            .offset(skip).limit(limit).all()
    
    def create(self, execution_data: Dict[str, Any]) -> Execution:
        """Create a new execution"""
        execution = Execution(**execution_data)
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution
    
    def update(self, execution_id: str, execution_data: Dict[str, Any]) -> Optional[Execution]:
        """Update an execution"""
        execution = self.get_by_id(execution_id)
        if not execution:
            return None
        
        # Update fields
        for key, value in execution_data.items():
            setattr(execution, key, value)
        
        self.db.commit()
        self.db.refresh(execution)
        return execution


class DeploymentRepository:
    """Repository for Deployment entities"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, deployment_id: str) -> Optional[Deployment]:
        """Get a deployment by ID"""
        return self.db.query(Deployment).filter(Deployment.id == deployment_id).first()
    
    def get_by_flow_id(self, flow_id: str) -> List[Deployment]:
        """Get deployments for a flow"""
        return self.db.query(Deployment).filter(Deployment.flow_id == flow_id).all()
    
    def create(self, deployment_data: Dict[str, Any]) -> Deployment:
        """Create a new deployment"""
        deployment = Deployment(**deployment_data)
        self.db.add(deployment)
        self.db.commit()
        self.db.refresh(deployment)
        return deployment
    
    def update(self, deployment_id: str, deployment_data: Dict[str, Any]) -> Optional[Deployment]:
        """Update a deployment"""
        deployment = self.get_by_id(deployment_id)
        if not deployment:
            return None
        
        # Update fields
        for key, value in deployment_data.items():
            setattr(deployment, key, value)
        
        self.db.commit()
        self.db.refresh(deployment)
        return deployment


class WebhookRepository:
    """Repository for Webhook entities"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_deployment_id(self, deployment_id: str) -> List[Webhook]:
        """Get webhooks for a deployment"""
        return self.db.query(Webhook).filter(Webhook.deployment_id == deployment_id).all()
    
    def create(self, webhook_data: Dict[str, Any]) -> Webhook:
        """Create a new webhook"""
        webhook = Webhook(**webhook_data)
        self.db.add(webhook)
        self.db.commit()
        self.db.refresh(webhook)
        return webhook
