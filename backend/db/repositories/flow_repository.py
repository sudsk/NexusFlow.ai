# backend/db/repositories/flow_repository.py (updated)
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..models.flow_model import FlowModel
from ...core.entities.flow import Flow

class FlowRepository:
    """Repository for Flow entities"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        name: Optional[str] = None,
        framework: Optional[str] = None
    ) -> List[Flow]:
        """Get all flows with optional filtering"""
        query = self.db.query(FlowModel)
        
        if name:
            query = query.filter(or_(
                FlowModel.name.ilike(f"%{name}%"),
                FlowModel.description.ilike(f"%{name}%")
            ))
        
        if framework:
            query = query.filter(FlowModel.framework == framework)
        
        flow_models = query.offset(skip).limit(limit).all()
        return [self._map_to_entity(model) for model in flow_models]
    
    def get_by_id(self, flow_id: str) -> Optional[Flow]:
        """Get a flow by ID"""
        flow_model = self.db.query(FlowModel).filter(FlowModel.id == flow_id).first()
        if not flow_model:
            return None
        return self._map_to_entity(flow_model)
    
    def create(self, flow: Flow) -> Flow:
        """Create a new flow"""
        flow_model = FlowModel(
            id=flow.flow_id,
            name=flow.name,
            description=flow.description,
            framework=flow.framework,
            config={
                "agents": flow.agents,
                "max_steps": flow.max_steps,
                "tools": flow.tools
            }
        )
        self.db.add(flow_model)
        self.db.commit()
        self.db.refresh(flow_model)
        return self._map_to_entity(flow_model)
    
    def update(self, flow: Flow) -> Optional[Flow]:
        """Update an existing flow"""
        flow_model = self.db.query(FlowModel).filter(FlowModel.id == flow.flow_id).first()
        if not flow_model:
            return None
        
        flow_model.name = flow.name
        flow_model.description = flow.description
        flow_model.framework = flow.framework
        flow_model.config = {
            "agents": flow.agents,
            "max_steps": flow.max_steps,
            "tools": flow.tools
        }
        
        self.db.commit()
        self.db.refresh(flow_model)
        return self._map_to_entity(flow_model)
    
    def delete(self, flow_id: str) -> bool:
        """Delete a flow"""
        flow_model = self.db.query(FlowModel).filter(FlowModel.id == flow_id).first()
        if not flow_model:
            return False
        
        self.db.delete(flow_model)
        self.db.commit()
        return True
    
    def _map_to_entity(self, model: FlowModel) -> Flow:
        """Map database model to domain entity"""
        config = model.config or {}
        return Flow(
            flow_id=model.id,
            name=model.name,
            description=model.description,
            agents=config.get("agents", []),
            max_steps=config.get("max_steps", 10),
            tools=config.get("tools", {}),
            framework=model.framework,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def count_flows(
        self, 
        name: Optional[str] = None,
        framework: Optional[str] = None
    ) -> int:
        """
        Count flows with optional filtering
        
        Args:
            name: Optional name filter
            framework: Optional framework filter
            
        Returns:
            Total number of flows matching the filter
        """
        query = self.db.query(FlowModel)
        
        if name:
            query = query.filter(or_(
                FlowModel.name.ilike(f"%{name}%"),
                FlowModel.description.ilike(f"%{name}%")
            ))
        
        if framework:
            query = query.filter(FlowModel.framework == framework)
        
        return query.count()
