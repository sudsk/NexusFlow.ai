# backend/adapters/interfaces/base_adapter.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Awaitable

class FrameworkAdapter(ABC):
    """Base interface for all AI orchestration framework adapters"""
    
    @abstractmethod
    def get_framework_name(self) -> str:
        """Return the name of the framework"""
        pass
    
    @abstractmethod
    def convert_flow(self, flow_config: Dict[str, Any]) -> Any:
        """
        Convert NexusFlow configuration to framework-specific flow
        
        Args:
            flow_config: Common flow configuration format
            
        Returns:
            Framework-specific flow object or configuration
        """
        pass
    
    @abstractmethod
    async def execute_flow(
        self, 
        flow: Any, 
        input_data: Dict[str, Any],
        step_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """
        Execute a framework flow with the given input data
        
        Args:
            flow: Framework-specific flow object
            input_data: Input data for the flow
            step_callback: Optional callback function to receive execution step updates
            
        Returns:
            Dictionary containing execution results
        """
        pass
    
    @abstractmethod
    def register_tools(
        self, 
        tools: List[Dict[str, Any]], 
        framework_config: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Register tools with the framework
        
        Args:
            tools: List of tool configurations
            framework_config: Optional framework-specific configuration
            
        Returns:
            Framework-specific tool registry or configuration
        """
        pass
    
    @abstractmethod
    def get_supported_features(self) -> Dict[str, bool]:
        """
        Return features supported by this framework
        
        Returns:
            Dictionary of feature flags
        """
        pass
    
    def validate_flow(self, flow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a flow configuration for this framework
        
        Args:
            flow_config: Flow configuration to validate
            
        Returns:
            Dictionary with validation results
        """
        # Default implementation - can be overridden by framework-specific adapters
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Basic checks
        if not flow_config.get("name"):
            validation_result["errors"].append("Flow name is required")
            validation_result["valid"] = False
            
        if not flow_config.get("agents") or len(flow_config.get("agents", [])) == 0:
            validation_result["errors"].append("At least one agent is required")
            validation_result["valid"] = False
            
        # Check framework-specific requirements
        supported_features = self.get_supported_features()
        
        # Multi-agent support
        if len(flow_config.get("agents", [])) > 1 and not supported_features.get("multi_agent", False):
            validation_result["errors"].append(f"Framework '{self.get_framework_name()}' does not support multiple agents")
            validation_result["valid"] = False
            
        # Tool support
        if flow_config.get("tools") and not supported_features.get("tools", False):
            validation_result["warnings"].append(f"Framework '{self.get_framework_name()}' does not support tools")
        
        return validation_result
    
    def get_default_agent_config(self) -> Dict[str, Any]:
        """
        Get default configuration for an agent in this framework
        
        Returns:
            Dictionary with default agent configuration
        """
        # Default implementation - can be overridden by framework-specific adapters
        return {
            "name": "Default Agent",
            "description": "Default agent for " + self.get_framework_name(),
            "model_provider": "openai",
            "model_name": "gpt-4",
            "temperature": 0.7,
            "system_message": "",
            "capabilities": [],
            "tool_names": []
        }
        
    def get_execution_info(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract standardized information from execution results
        
        Args:
            execution_result: Framework-specific execution result
            
        Returns:
            Standardized execution information dictionary
        """
        # Default implementation - can be overridden by framework-specific adapters
        return {
            "output": execution_result.get("output", {}),
            "steps": len(execution_result.get("execution_trace", [])),
            "status": execution_result.get("status", "completed"),
            "metadata": {
                "framework": self.get_framework_name()
            }
        }
        
    async def visualize_flow(
        self, 
        flow: Any, 
        format: str = "json",
        include_tools: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a visualization of the flow
        
        Args:
            flow: Framework-specific flow object
            format: Desired format ('json', 'mermaid', 'dot')
            include_tools: Whether to include tool nodes
            
        Returns:
            Dictionary containing visualization data
        """
        # Default implementation - can be overridden by framework-specific adapters
        # Most minimal implementation that returns a JSON structure
        agents = []
        connections = []
        
        # Extract agents from the flow
        if isinstance(flow, dict) and flow.get("agents"):
            for i, agent in enumerate(flow.get("agents", [])):
                agents.append({
                    "id": agent.get("agent_id", f"agent-{i}"),
                    "name": agent.get("name", f"Agent {i+1}"),
                    "type": "agent"
                })
                
            # Create connections between agents (simple linear chain by default)
            for i in range(len(agents) - 1):
                connections.append({
                    "source": agents[i]["id"],
                    "target": agents[i+1]["id"],
                    "type": "default"
                })
                
        # Add tool nodes if requested
        if include_tools and isinstance(flow, dict) and flow.get("tools"):
            tool_nodes = []
            for tool_name, tool_config in flow.get("tools", {}).items():
                tool_id = f"tool-{tool_name}"
                tool_nodes.append({
                    "id": tool_id,
                    "name": tool_name,
                    "type": "tool",
                    "description": tool_config.get("description", "")
                })
                
                # Connect tools to agents that use them
                for agent in flow.get("agents", []):
                    if tool_name in agent.get("tool_names", []):
                        connections.append({
                            "source": agent.get("agent_id", f"agent-{flow.get('agents').index(agent)}"),
                            "target": tool_id,
                            "type": "tool",
                            "bidirectional": True
                        })
                        
            agents.extend(tool_nodes)
                
        return {
            "nodes": agents,
            "edges": connections,
            "framework": self.get_framework_name(),
            "format": format
        }
