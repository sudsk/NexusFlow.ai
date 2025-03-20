# backend/core/entities/flow.py (updated)
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

class Flow:
    """Core flow entity"""
    
    def __init__(
        self, 
        name: str,
        description: Optional[str] = None,
        agents: Optional[List[Dict[str, Any]]] = None,
        max_steps: int = 10,
        tools: Optional[Dict[str, Any]] = None,
        framework: str = "langgraph",
        flow_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.flow_id = flow_id or str(uuid.uuid4())
        self.name = name
        self.description = description or ""
        self.agents = agents or []
        self.max_steps = max_steps
        self.tools = tools or {}
        self.framework = framework
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert flow to dictionary representation"""
        return {
            "flow_id": self.flow_id,
            "name": self.name,
            "description": self.description,
            "agents": self.agents,
            "max_steps": self.max_steps,
            "tools": self.tools,
            "framework": self.framework,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Flow':
        """Create flow from dictionary"""
        created_at = data.get('created_at')
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
            
        updated_at = data.get('updated_at')
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
            
        return cls(
            flow_id=data.get('flow_id'),
            name=data.get('name', 'Unnamed Flow'),
            description=data.get('description'),
            agents=data.get('agents', []),
            max_steps=data.get('max_steps', 10),
            tools=data.get('tools', {}),
            framework=data.get('framework', 'langgraph'),
            created_at=created_at,
            updated_at=updated_at
        )
