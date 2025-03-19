# backend/services/flow/flow_service.py
from typing import Dict, List, Any, Optional
from ...core.entities.flow import Flow
from ...db.repositories.flow_repository import FlowRepository
from ...adapters.interfaces.base_adapter import FrameworkAdapter

class FlowService:
    """Service for managing flows"""
    
    def __init__(self, flow_repository: FlowRepository, adapter_registry: Dict[str, FrameworkAdapter]):
        self.flow_repository = flow_repository
        self.adapter_registry = adapter_registry
    
    async def create_flow(self, flow_data: Dict[str, Any]) -> Flow:
        """Create a new flow"""
        flow = Flow(
            name=flow_data.get("name", "Unnamed Flow"),
            description=flow_data.get("description"),
            agents=flow_data.get("agents", []),
            max_steps=flow_data.get("max_steps", 10),
            tools=flow_data.get("tools", {})
        )
        return self.flow_repository.create(flow)
    
    async def get_flow(self, flow_id: str) -> Optional[Flow]:
        """Get a flow by ID"""
        return self.flow_repository.get_by_id(flow_id)
    
    async def update_flow(self, flow_id: str, flow_data: Dict[str, Any]) -> Optional[Flow]:
        """Update a flow"""
        existing_flow = self.flow_repository.get_by_id(flow_id)
        if not existing_flow:
            return None
            
        updated_flow = Flow(
            flow_id=flow_id,
            name=flow_data.get("name", existing_flow.name),
            description=flow_data.get("description", existing_flow.description),
            agents=flow_data.get("agents", existing_flow.agents),
            max_steps=flow_data.get("max_steps", existing_flow.max_steps),
            tools=flow_data.get("tools", existing_flow.tools)
        )
        
        return self.flow_repository.update(updated_flow)
    
    async def delete_flow(self, flow_id: str) -> bool:
        """Delete a flow"""
        return self.flow_repository.delete(flow_id)
    
    async def list_flows(self, skip: int = 0, limit: int = 100, name: Optional[str] = None) -> List[Flow]:
        """List flows with filtering"""
        return self.flow_repository.get_all(skip, limit, name)
    
    async def execute_flow(self, flow_id: str, input_data: Dict[str, Any], framework: str = "langgraph") -> Dict[str, Any]:
        """Execute a flow with the selected framework"""
        # Get flow from repository
        flow = self.flow_repository.get_by_id(flow_id)
        if not flow:
            raise ValueError(f"Flow with ID {flow_id} not found")
        
        # Get adapter for the specified framework
        if framework not in self.adapter_registry:
            raise ValueError(f"Framework '{framework}' not supported")
        
        adapter = self.adapter_registry[framework]
        
        # Convert flow to framework-specific format
        framework_flow = adapter.convert_flow(flow.to_dict())
        
        # Execute flow
        result = await adapter.execute_flow(framework_flow, input_data)
        
        return result
