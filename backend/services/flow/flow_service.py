# backend/services/flow/flow_service.py
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from ...core.entities.flow import Flow
from ...db.repositories.flow_repository import FlowRepository
from ...adapters.registry import get_adapter_registry

logger = logging.getLogger(__name__)

class FlowService:
    """Service for managing flows"""
    
    def __init__(self, flow_repository: FlowRepository):
        self.flow_repository = flow_repository
        self.adapter_registry = get_adapter_registry()
    
    async def create_flow(self, flow_data: Dict[str, Any]) -> Flow:
        """
        Create a new flow
        
        Args:
            flow_data: Flow data
            
        Returns:
            Created flow
        """
        # Check if framework is specified and valid
        framework = flow_data.get("framework")
        if framework:
            try:
                self.adapter_registry.get_adapter(framework)
            except ValueError:
                logger.warning(f"Invalid framework '{framework}', defaulting to 'langgraph'")
                flow_data["framework"] = "langgraph"
        else:
            # Default to langgraph if no framework is specified
            flow_data["framework"] = "langgraph"
        
        # Create Flow entity
        flow = Flow(
            name=flow_data.get("name", "Untitled Flow"),
            description=flow_data.get("description"),
            agents=flow_data.get("agents", []),
            max_steps=flow_data.get("max_steps", 10),
            tools=flow_data.get("tools", {}),
            framework=flow_data.get("framework", "langgraph")
        )
        
        # Persist to database
        created_flow = self.flow_repository.create(flow)
        
        return created_flow
    
    async def get_flow(self, flow_id: str) -> Optional[Flow]:
        """
        Get a flow by ID
        
        Args:
            flow_id: ID of the flow
            
        Returns:
            Flow or None if not found
        """
        return self.flow_repository.get_by_id(flow_id)
    
    async def update_flow(self, flow_id: str, flow_data: Dict[str, Any]) -> Optional[Flow]:
        """
        Update an existing flow
        
        Args:
            flow_id: ID of the flow
            flow_data: Updated flow data
            
        Returns:
            Updated flow or None if not found
        """
        # Check if framework is specified and valid
        framework = flow_data.get("framework")
        if framework:
            try:
                self.adapter_registry.get_adapter(framework)
            except ValueError:
                logger.warning(f"Invalid framework '{framework}', using existing or defaulting to 'langgraph'")
                flow_data.pop("framework", None)
        
        # Get existing flow
        existing_flow = self.flow_repository.get_by_id(flow_id)
        if not existing_flow:
            return None
        
        # Update fields
        for key, value in flow_data.items():
            setattr(existing_flow, key, value)
        
        # Persist updates
        updated_flow = self.flow_repository.update(existing_flow)
        
        return updated_flow
    
    async def delete_flow(self, flow_id: str) -> bool:
        """
        Delete a flow
        
        Args:
            flow_id: ID of the flow
            
        Returns:
            True if deleted, False if not found
        """
        return self.flow_repository.delete(flow_id)
    
    async def list_flows(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        name: Optional[str] = None,
        framework: Optional[str] = None
    ) -> List[Flow]:
        """
        List flows with optional filtering
        
        Args:
            skip: Number of flows to skip
            limit: Maximum number of flows to return
            name: Optional filter by name
            framework: Optional filter by framework
            
        Returns:
            List of flows
        """
        return self.flow_repository.get_all(skip=skip, limit=limit, name=name, framework=framework)

    async def count_flows(
        self, 
        name: Optional[str] = None,
        framework: Optional[str] = None
    ) -> int:
        """
        Count flows with optional filtering
        
        Args:
            name: Optional filter by name
            framework: Optional filter by framework
            
        Returns:
            Total number of flows matching the filter
        """
        return self.flow_repository.count_flows(name=name, framework=framework)
    
    
    async def get_frameworks(self) -> Dict[str, Dict[str, bool]]:
        """
        Get information about available frameworks
        
        Returns:
            Dictionary of framework information
        """
        return self.adapter_registry.get_available_frameworks()
    
    async def validate_flow(self, flow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a flow configuration
        
        Args:
            flow_config: Flow configuration to validate
            
        Returns:
            Validation results
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        if not flow_config.get("name"):
            validation_results["errors"].append("Flow name is required")
            validation_results["valid"] = False
        
        # Check agents
        agents = flow_config.get("agents", [])
        if not agents:
            validation_results["errors"].append("At least one agent is required")
            validation_results["valid"] = False
        else:
            # Check each agent
            for i, agent in enumerate(agents):
                if not agent.get("name"):
                    validation_results["errors"].append(f"Agent at index {i} missing required field 'name'")
                    validation_results["valid"] = False
        
        # Check framework
        framework = flow_config.get("framework", "langgraph")
        try:
            adapter = self.adapter_registry.get_adapter(framework)
            # Check if framework supports multi-agent if multiple agents
            if len(agents) > 1:
                features = adapter.get_supported_features()
                if not features.get("multi_agent", False):
                    validation_results["warnings"].append(
                        f"Framework '{framework}' may not fully support multi-agent flows"
                    )
        except ValueError:
            validation_results["errors"].append(f"Unsupported framework: {framework}")
            validation_results["valid"] = False
        
        return validation_results
    
    async def export_flow(self, flow_id: str, target_framework: Optional[str] = None) -> Dict[str, Any]:
        """
        Export a flow to a specific framework format
        
        Args:
            flow_id: ID of the flow
            target_framework: Target framework (default is the flow's framework)
            
        Returns:
            Exported flow configuration
        """
        # Get flow
        flow = self.flow_repository.get_by_id(flow_id)
        if not flow:
            raise ValueError(f"Flow with ID {flow_id} not found")
        
        # If no target framework specified, use the flow's framework
        if not target_framework:
            target_framework = flow.framework if hasattr(flow, 'framework') and flow.framework else "langgraph"
        
        # Get adapter for target framework
        try:
            adapter = self.adapter_registry.get_adapter(target_framework)
        except ValueError:
            raise ValueError(f"Unsupported framework: {target_framework}")
        
        # Convert flow to target framework format
        flow_dict = flow.to_dict()
        converted_flow = adapter.convert_flow(flow_dict)
        
        return {
            "flow_id": flow_id,
            "original_framework": flow.framework if hasattr(flow, 'framework') else "langgraph",
            "target_framework": target_framework,
            "exported_config": converted_flow
        }
