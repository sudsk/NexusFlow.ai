# backend/services/tool/tool_service.py
from typing import Dict, List, Any, Optional
import json
import logging
import importlib
import inspect
from datetime import datetime

from ...db.repositories.tool_repository import ToolRepository

logger = logging.getLogger(__name__)

class ToolService:
    """Service for managing tools and their configurations"""
    
    def __init__(self, tool_repository: ToolRepository):
        self.tool_repository = tool_repository
        self._tool_cache = {}  # Cache loaded tool implementations
    
    async def get_all_tools(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        name_filter: Optional[str] = None,
        framework: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all available tools with optional filtering
        
        Args:
            skip: Number of tools to skip
            limit: Maximum number of tools to return
            name_filter: Filter by name or description
            framework: Filter by framework compatibility
            
        Returns:
            List of tool dictionaries
        """
        tools = self.tool_repository.get_all(skip, limit, name_filter)
        
        # Convert to dictionaries
        tool_dicts = [self._convert_to_dict(tool) for tool in tools]
        
        # Apply framework filter if specified
        if framework:
            tool_dicts = [
                tool for tool in tool_dicts 
                if not tool.get('metadata', {}).get('compatible_frameworks') or
                framework in tool.get('metadata', {}).get('compatible_frameworks', [])
            ]
            
        return tool_dicts
    
    async def get_tool_by_id(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a tool by ID
        
        Args:
            tool_id: ID of the tool
            
        Returns:
            Tool dictionary or None if not found
        """
        tool = self.tool_repository.get_by_id(tool_id)
        return self._convert_to_dict(tool) if tool else None
    
    async def get_tool_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a tool by name
        
        Args:
            name: Name of the tool
            
        Returns:
            Tool dictionary or None if not found
        """
        tool = self.tool_repository.get_by_name(name)
        return self._convert_to_dict(tool) if tool else None
    
    async def create_tool(self, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new tool
        
        Args:
            tool_data: Tool data including name, description, parameters, etc.
            
        Returns:
            Created tool as dictionary
        """
        # Validate tool data
        self._validate_tool_data(tool_data)
        
        # Ensure parameters is a valid JSON object
        if "parameters" not in tool_data or not isinstance(tool_data["parameters"], dict):
            tool_data["parameters"] = {}
            
        # Set default values for optional fields
        if "metadata" not in tool_data or not isinstance(tool_data["metadata"], dict):
            tool_data["metadata"] = {}
            
        # Create the tool
        tool = self.tool_repository.create(tool_data)
        
        # Clear cache if tool implementation exists
        self._clear_tool_cache(tool_data.get('name'))
        
        return self._convert_to_dict(tool)
    
    async def update_tool(self, tool_id: str, tool_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing tool
        
        Args:
            tool_id: ID of the tool to update
            tool_data: Updated tool data
            
        Returns:
            Updated tool dictionary or None if not found
        """
        # Get existing tool
        existing_tool = self.tool_repository.get_by_id(tool_id)
        if not existing_tool:
            return None
            
        # Validate tool data if name or parameters are changing
        if 'name' in tool_data or 'parameters' in tool_data:
            # Create merged data for validation
            merged_data = {**self._convert_to_dict(existing_tool), **tool_data}
            self._validate_tool_data(merged_data)
        
        # Update the tool
        updated_tool = self.tool_repository.update(tool_id, tool_data)
        
        # Clear cache if name is changing or the same name
        if 'name' in tool_data:
            self._clear_tool_cache(tool_data['name'])
            self._clear_tool_cache(existing_tool.name)
        else:
            self._clear_tool_cache(existing_tool.name)
        
        return self._convert_to_dict(updated_tool) if updated_tool else None
    
    async def delete_tool(self, tool_id: str) -> bool:
        """
        Delete a tool
        
        Args:
            tool_id: ID of the tool to delete
            
        Returns:
            True if deleted, False if not found
        """
        # Get tool name before deletion for cache clearing
        tool = self.tool_repository.get_by_id(tool_id)
        tool_name = tool.name if tool else None
        
        # Delete the tool
        success = self.tool_repository.delete(tool_id)
        
        # Clear cache if tool existed
        if success and tool_name:
            self._clear_tool_cache(tool_name)
            
        return success
    
    async def get_tool_function(self, tool_name: str) -> Optional[Any]:
        """
        Get the implementation function for a tool
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Function implementation or None if not found
        """
        # Check cache first
        if tool_name in self._tool_cache:
            return self._tool_cache[tool_name]
            
        # Get tool from database
        tool = self.tool_repository.get_by_name(tool_name)
        if not tool or not tool.function_name:
            return None
            
        try:
            # Try to import and find the function
            # Format should be: module_path.function_name or just function_name
            if '.' in tool.function_name:
                # Module path provided
                module_path, func_name = tool.function_name.rsplit('.', 1)
                module = importlib.import_module(module_path)
                func = getattr(module, func_name)
            else:
                # Look in default tools module
                try:
                    module = importlib.import_module('...tools.default_tools', package=__name__)
                    func = getattr(module, tool.function_name)
                except (ImportError, AttributeError):
                    # Try looking in custom tools module
                    module = importlib.import_module('...tools.custom_tools', package=__name__)
                    func = getattr(module, tool.function_name)
            
            # Cache the function
            self._tool_cache[tool_name] = func
            return func
            
        except (ImportError, AttributeError) as e:
            logger.error(f"Error loading tool implementation for {tool_name}: {str(e)}")
            return None
    
    async def execute_tool(
        self,
        tool_name: str, 
        params: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool with the given parameters
        
        Args:
            tool_name: Name of the tool to execute
            params: Parameters for the tool
            context: Additional context for execution
            
        Returns:
            Tool execution result
        """
        # Get tool
        tool = self.tool_repository.get_by_name(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
            
        # Check if tool is enabled
        if not tool.is_enabled:
            raise ValueError(f"Tool '{tool_name}' is disabled")
            
        # Get tool function
        func = await self.get_tool_function(tool_name)
        if not func:
            raise ValueError(f"Implementation for tool '{tool_name}' not found")
            
        # Validate parameters against schema
        self._validate_parameters(params, tool.parameters)
        
        # Prepare context
        execution_context = context or {}
        
        try:
            # Execute the tool
            start_time = datetime.utcnow()
            
            # Check if function accepts context
            sig = inspect.signature(func)
            if 'context' in sig.parameters:
                result = func(params, context=execution_context)
            else:
                result = func(params)
                
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Format response
            return {
                "result": result,
                "tool": tool_name,
                "duration": duration,
                "status": "success"
            }
        except Exception as e:
            logger.exception(f"Error executing tool {tool_name}: {str(e)}")
            return {
                "error": str(e),
                "tool": tool_name,
                "status": "error"
            }
    
    async def get_available_tools_for_flow(
        self,
        framework: str,
        enabled_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get tools available for a specific framework
        
        Args:
            framework: Framework name
            enabled_only: Only return enabled tools
            
        Returns:
            List of tool dictionaries
        """
        # Get all tools
        tools = self.tool_repository.get_all()
        
        # Filter by framework compatibility and enabled status
        filtered_tools = []
        for tool in tools:
            tool_dict = self._convert_to_dict(tool)
            
            # Check if enabled (if filter is on)
            if enabled_only and not tool.is_enabled:
                continue
                
            # Check framework compatibility
            compatible_frameworks = tool_dict.get('metadata', {}).get('compatible_frameworks', [])
            if not compatible_frameworks or framework in compatible_frameworks:
                filtered_tools.append(tool_dict)
                
        return filtered_tools
        
    def _validate_tool_data(self, tool_data: Dict[str, Any]) -> None:
        """
        Validate tool data for creation or update
        
        Args:
            tool_data: Tool data to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Check required fields
        if 'name' not in tool_data or not tool_data['name']:
            raise ValueError("Tool name is required")
            
        if 'description' not in tool_data or not tool_data['description']:
            raise ValueError("Tool description is required")
            
        # Validate parameters schema if provided
        if 'parameters' in tool_data and tool_data['parameters']:
            try:
                # Basic JSON Schema validation
                if not isinstance(tool_data['parameters'], dict):
                    raise ValueError("Parameters must be a valid JSON schema object")
                    
                if 'type' not in tool_data['parameters']:
                    raise ValueError("Parameters schema must include 'type' field")
                    
                if tool_data['parameters']['type'] != 'object':
                    raise ValueError("Parameters schema 'type' must be 'object'")
                    
            except Exception as e:
                raise ValueError(f"Invalid parameters schema: {str(e)}")
    
    def _validate_parameters(self, params: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """
        Validate parameters against schema
        
        Args:
            params: Parameters to validate
            schema: JSON Schema to validate against
            
        Raises:
            ValueError: If validation fails
        """
        # Simple validation for MVP - can be expanded later
        if not schema:
            return
            
        # Check required fields
        required = schema.get('required', [])
        for field in required:
            if field not in params:
                raise ValueError(f"Required parameter '{field}' is missing")
                
        # Check parameter types (basic)
        properties = schema.get('properties', {})
        for param_name, param_value in params.items():
            if param_name in properties:
                param_schema = properties[param_name]
                param_type = param_schema.get('type')
                
                if param_type == 'string' and not isinstance(param_value, str):
                    raise ValueError(f"Parameter '{param_name}' must be a string")
                    
                elif param_type == 'number' and not isinstance(param_value, (int, float)):
                    raise ValueError(f"Parameter '{param_name}' must be a number")
                    
                elif param_type == 'integer' and not isinstance(param_value, int):
                    raise ValueError(f"Parameter '{param_name}' must be an integer")
                    
                elif param_type == 'boolean' and not isinstance(param_value, bool):
                    raise ValueError(f"Parameter '{param_name}' must be a boolean")
                    
                elif param_type == 'array' and not isinstance(param_value, list):
                    raise ValueError(f"Parameter '{param_name}' must be an array")
                    
                elif param_type == 'object' and not isinstance(param_value, dict):
                    raise ValueError(f"Parameter '{param_name}' must be an object")
    
    def _convert_to_dict(self, tool) -> Dict[str, Any]:
        """Convert tool model to dictionary"""
        if not tool:
            return None
            
        # Parse JSON fields if stored as strings
        parameters = tool.parameters
        if isinstance(parameters, str):
            try:
                parameters = json.loads(parameters)
            except (json.JSONDecodeError, TypeError):
                parameters = {}
                
        metadata = tool.metadata
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except (json.JSONDecodeError, TypeError):
                metadata = {}
        
        return {
            "id": tool.id,
            "name": tool.name,
            "description": tool.description,
            "parameters": parameters,
            "function_name": tool.function_name,
            "is_enabled": tool.is_enabled,
            "requires_authentication": tool.requires_authentication,
            "created_at": tool.created_at.isoformat() if tool.created_at else None,
            "updated_at": tool.updated_at.isoformat() if tool.updated_at else None,
            "metadata": metadata or {}
        }
        
    def _clear_tool_cache(self, tool_name: str) -> None:
        """
        Clear the tool function cache for a specific tool
        
        Args:
            tool_name: Name of the tool to clear from cache
        """
        if tool_name in self._tool_cache:
            del self._tool_cache[tool_name]
