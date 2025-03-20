# backend/services/flow/validator_service.py
from typing import Dict, List, Any, Optional
import logging
import jsonschema
from ..tool.registry_service import get_tool_registry
from ...adapters.registry import get_adapter_registry

logger = logging.getLogger(__name__)

class FlowValidator:
    """Service for validating flow configurations before execution or saving"""
    
    def __init__(self):
        self.tool_registry = get_tool_registry()
        self.adapter_registry = get_adapter_registry()
        
    def validate_flow(self, flow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a flow configuration
        
        Args:
            flow_config: Flow configuration to validate
            
        Returns:
            Validation results with errors and warnings
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Basic schema validation
        schema_validation = self._validate_schema(flow_config)
        if not schema_validation["valid"]:
            validation_results["valid"] = False
            validation_results["errors"].extend(schema_validation["errors"])
        
        # Validate framework
        framework_validation = self._validate_framework(flow_config)
        if not framework_validation["valid"]:
            validation_results["valid"] = False
            validation_results["errors"].extend(framework_validation["errors"])
        validation_results["warnings"].extend(framework_validation["warnings"])
        
        # Validate agents
        agent_validation = self._validate_agents(flow_config)
        if not agent_validation["valid"]:
            validation_results["valid"] = False
            validation_results["errors"].extend(agent_validation["errors"])
        validation_results["warnings"].extend(agent_validation["warnings"])
        
        # Validate tools
        tool_validation = self._validate_tools(flow_config)
        if not tool_validation["valid"]:
            validation_results["valid"] = False
            validation_results["errors"].extend(tool_validation["errors"])
        validation_results["warnings"].extend(tool_validation["warnings"])
        
        # Additional adapter-specific validation
        if validation_results["valid"]:
            framework = flow_config.get("framework", "langgraph")
            try:
                adapter = self.adapter_registry.get_adapter(framework)
                adapter_validation = adapter.validate_flow(flow_config)
                
                if not adapter_validation.get("valid", True):
                    validation_results["valid"] = False
                    validation_results["errors"].extend(adapter_validation.get("errors", []))
                
                validation_results["warnings"].extend(adapter_validation.get("warnings", []))
                
            except Exception as e:
                logger.error(f"Error during adapter-specific validation: {str(e)}")
                validation_results["warnings"].append(f"Could not perform framework-specific validation: {str(e)}")
        
        return validation_results
    
    def _validate_schema(self, flow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate flow configuration against basic schema
        
        Args:
            flow_config: Flow configuration to validate
            
        Returns:
            Validation results
        """
        result = {
            "valid": True,
            "errors": []
        }
        
        # Define basic schema for flow validation
        schema = {
            "type": "object",
            "required": ["name", "agents"],
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "description": {"type": "string"},
                "framework": {"type": "string"},
                "max_steps": {"type": "integer", "minimum": 1},
                "agents": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string", "minLength": 1},
                            "agent_id": {"type": "string"},
                            "model_provider": {"type": "string"},
                            "model_name": {"type": "string"},
                            "system_message": {"type": "string"},
                            "temperature": {"type": "number", "minimum": 0, "maximum": 1},
                            "capabilities": {"type": "array", "items": {"type": "string"}},
                            "tool_names": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                },
                "tools": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "config": {"type": "object"}
                        }
                    }
                }
            }
        }
        
        # Validate against schema
        try:
            jsonschema.validate(instance=flow_config, schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            result["valid"] = False
            # Format error message to be more user-friendly
            error_path = "/".join(str(p) for p in e.path)
            if error_path:
                result["errors"].append(f"Schema validation error at '{error_path}': {e.message}")
            else:
                result["errors"].append(f"Schema validation error: {e.message}")
        
        return result
    
    def _validate_framework(self, flow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate framework configuration
        
        Args:
            flow_config: Flow configuration to validate
            
        Returns:
            Validation results
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        framework = flow_config.get("framework")
        if not framework:
            # Default to langgraph if not specified
            return result
        
        # Check if framework is supported
        try:
            self.adapter_registry.get_adapter(framework)
        except ValueError:
            result["valid"] = False
            result["errors"].append(f"Framework '{framework}' is not supported")
            result["warnings"].append(f"Supported frameworks: {', '.join(self.adapter_registry.get_available_frameworks().keys())}")
        
        return result
    
    def _validate_agents(self, flow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate agent configurations
        
        Args:
            flow_config: Flow configuration to validate
            
        Returns:
            Validation results
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        agents = flow_config.get("agents", [])
        
        # Check if agents exist
        if not agents:
            result["valid"] = False
            result["errors"].append("Flow must have at least one agent")
            return result
        
        # Check for duplicate agent IDs
        agent_ids = []
        for i, agent in enumerate(agents):
            agent_id = agent.get("agent_id")
            if not agent_id:
                # Generate a warning for missing agent_id
                result["warnings"].append(f"Agent at index {i} is missing an agent_id")
            elif agent_id in agent_ids:
                result["valid"] = False
                result["errors"].append(f"Duplicate agent_id '{agent_id}' found")
            else:
                agent_ids.append(agent_id)
            
            # Check for required fields
            if not agent.get("name"):
                result["valid"] = False
                result["errors"].append(f"Agent at index {i} is missing required name")
            
            # Check model configuration
            if not agent.get("model_provider"):
                result["warnings"].append(f"Agent '{agent.get('name', f'at index {i}')}' missing model_provider")
                
            if not agent.get("model_name"):
                result["warnings"].append(f"Agent '{agent.get('name', f'at index {i}')}' missing model_name")
        
        # Check framework compatibility with multiple agents
        if len(agents) > 1:
            framework = flow_config.get("framework", "langgraph")
            try:
                adapter = self.adapter_registry.get_adapter(framework)
                features = adapter.get_supported_features()
                
                if not features.get("multi_agent", False):
                    result["warnings"].append(f"Framework '{framework}' may not fully support multiple agents")
            except ValueError:
                # Framework validation is handled elsewhere
                pass
        
        return result
    
    def _validate_tools(self, flow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate tool configurations and references
        
        Args:
            flow_config: Flow configuration to validate
            
        Returns:
            Validation results
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Get tools referenced by agents
        referenced_tools = set()
        for agent in flow_config.get("agents", []):
            for tool_name in agent.get("tool_names", []):
                referenced_tools.add(tool_name)
        
        # Get tools defined in flow
        defined_tools = set(flow_config.get("tools", {}).keys())
        
        # Check for tools referenced but not defined
        missing_tools = referenced_tools - defined_tools
        if missing_tools:
            # Try to find tools in registry
            for tool_name in missing_tools:
                registry_tool = self.tool_registry.get_tool(tool_name)
                if registry_tool:
                    # Tool exists in registry but not in flow definition
                    result["warnings"].append(f"Tool '{tool_name}' is referenced but not defined in flow. It will be loaded from registry.")
                else:
                    # Tool doesn't exist in registry either
                    result["valid"] = False
                    result["errors"].append(f"Tool '{tool_name}' is referenced but not defined in flow or registry")
        
        # Check for tools defined but not referenced
        unused_tools = defined_tools - referenced_tools
        if unused_tools:
            for tool_name in unused_tools:
                result["warnings"].append(f"Tool '{tool_name}' is defined but not referenced by any agent")
        
        # Check framework compatibility
        framework = flow_config.get("framework", "langgraph")
        try:
            adapter = self.adapter_registry.get_adapter(framework)
            features = adapter.get_supported_features()
            
            if not features.get("tools", False) and referenced_tools:
                result["warnings"].append(f"Framework '{framework}' may not support tools, but {len(referenced_tools)} tools are referenced")
        except ValueError:
            # Framework validation is handled elsewhere
            pass
        
        return result

# Singleton instance
_flow_validator = None

def get_flow_validator() -> FlowValidator:
    """
    Get the flow validator instance
    """
    global _flow_validator
    if _flow_validator is None:
        _flow_validator = FlowValidator()
    return _flow_validator
