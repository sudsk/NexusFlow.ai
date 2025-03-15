"""
Tool Registry for NexusFlow.ai

This module defines the ToolRegistry class, which manages all available tools for agents.
"""

from typing import Dict, List, Any, Optional, Union, Callable, Type, Awaitable
import logging
import inspect
import asyncio
import uuid
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ToolParameter:
    """Definition of a parameter for a tool"""
    
    def __init__(
        self,
        name: str,
        description: str,
        type: str = "string",
        required: bool = True,
        default: Any = None,
        enum: Optional[List[Any]] = None
    ):
        """
        Initialize a tool parameter
        
        Args:
            name: Name of the parameter
            description: Description of the parameter
            type: Type of the parameter (string, number, boolean, array, object)
            required: Whether the parameter is required
            default: Default value for the parameter
            enum: List of possible values for the parameter
        """
        self.name = name
        self.description = description
        self.type = type
        self.required = required
        self.default = default
        self.enum = enum
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parameter to dictionary representation"""
        param_dict = {
            "type": self.type,
            "description": self.description
        }
        
        if not self.required:
            param_dict["required"] = False
            
        if self.default is not None:
            param_dict["default"] = self.default
            
        if self.enum is not None:
            param_dict["enum"] = self.enum
            
        return param_dict
    
    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> 'ToolParameter':
        """Create parameter from dictionary"""
        return cls(
            name=name,
            description=data.get("description", ""),
            type=data.get("type", "string"),
            required=data.get("required", True),
            default=data.get("default"),
            enum=data.get("enum")
        )

class ToolDefinition:
    """Definition of a tool with its parameters and metadata"""
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Union[Dict[str, Any], ToolParameter]],
        handler: Optional[Callable] = None,
        function_name: Optional[str] = None,
        requires_confirmation: bool = False,
        requires_authentication: bool = False,
        is_async: Optional[bool] = None,
        category: str = "general",
        tags: List[str] = []
    ):
        """
        Initialize a tool definition
        
        Args:
            name: Name of the tool
            description: Description of what the tool does
            parameters: Dictionary of parameter definitions
            handler: Function to handle tool execution
            function_name: Name of the function (if different from tool name)
            requires_confirmation: Whether the tool requires confirmation before execution
            requires_authentication: Whether the tool requires authentication
            is_async: Whether the handler is async (auto-detected if handler is provided)
            category: Category of the tool
            tags: List of tags for the tool
        """
        self.name = name
        self.description = description
        
        # Process parameters
        self.parameters = {}
        for param_name, param_def in parameters.items():
            if isinstance(param_def, ToolParameter):
                self.parameters[param_name] = param_def
            else:
                self.parameters[param_name] = ToolParameter.from_dict(param_name, param_def)
        
        self.handler = handler
        self.function_name = function_name or name
        self.requires_confirmation = requires_confirmation
        self.requires_authentication = requires_authentication
        
        # Auto-detect if the handler is async
        if is_async is None and handler is not None:
            self.is_async = asyncio.iscoroutinefunction(handler) or hasattr(handler, "__await__")
        else:
            self.is_async = is_async or False
            
        self.category = category
        self.tags = tags
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool definition to dictionary representation"""
        parameters_schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param_name, param in self.parameters.items():
            parameters_schema["properties"][param_name] = param.to_dict()
            if param.required:
                parameters_schema["required"].append(param_name)
        
        return {
            "name": self.name,
            "description": self.description,
            "function_name": self.function_name,
            "parameters": parameters_schema,
            "requires_confirmation": self.requires_confirmation,
            "requires_authentication": self.requires_authentication,
            "is_async": self.is_async,
            "category": self.category,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], handler: Optional[Callable] = None) -> 'ToolDefinition':
        """Create tool definition from dictionary"""
        # Extract parameters from schema
        parameters = {}
        
        if "parameters" in data and "properties" in data["parameters"]:
            properties = data["parameters"]["properties"]
            required = data["parameters"].get("required", [])
            
            for param_name, param_data in properties.items():
                param_data["required"] = param_name in required
                parameters[param_name] = ToolParameter.from_dict(param_name, param_data)
        
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            parameters=parameters,
            handler=handler,
            function_name=data.get("function_name"),
            requires_confirmation=data.get("requires_confirmation", False),
            requires_authentication=data.get("requires_authentication", False),
            is_async=data.get("is_async"),
            category=data.get("category", "general"),
            tags=data.get("tags", [])
        )

class ToolResult:
    """Result of a tool execution"""
    
    def __init__(
        self,
        result: Any,
        success: bool = True,
        error: Optional[str] = None,
        execution_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a tool result
        
        Args:
            result: Result of the tool execution
            success: Whether the execution was successful
            error: Error message if execution failed
            execution_time: Time taken for execution in seconds
            metadata: Additional metadata about the execution
        """
        self.result = result
        self.success = success
        self.error = error
        self.execution_time = execution_time
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary representation"""
        return {
            "result": self.result,
            "success": self.success,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolResult':
        """Create result from dictionary"""
        return cls(
            result=data.get("result"),
            success=data.get("success", True),
            error=data.get("error"),
            execution_time=data.get("execution_time"),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def error(cls, error_message: str, metadata: Optional[Dict[str, Any]] = None) -> 'ToolResult':
        """Create an error result"""
        return cls(
            result=None,
            success=False,
            error=error_message,
            metadata=metadata
        )

class ToolRegistry:
    """Registry for all available tools"""
    
    def __init__(self):
        """Initialize a tool registry"""
        self.tools: Dict[str, ToolDefinition] = {}
        self.executions: List[Dict[str, Any]] = []
    
    def register_tool(self, tool: Union[ToolDefinition, Dict[str, Any]], handler: Optional[Callable] = None) -> None:
        """
        Register a tool with the registry
        
        Args:
            tool: Tool definition or dictionary
            handler: Function to handle tool execution (if not included in definition)
        """
        if isinstance(tool, dict):
            # Convert dictionary to ToolDefinition
            tool_def = ToolDefinition.from_dict(tool, handler)
        else:
            tool_def = tool
            if handler is not None:
                tool_def.handler = handler
        
        # Ensure handler is provided
        if tool_def.handler is None:
            logger.warning(f"Tool {tool_def.name} registered without a handler")
        
        # Register the tool
        self.tools[tool_def.name] = tool_def
        logger.info(f"Registered tool: {tool_def.name}")
    
    def unregister_tool(self, tool_name: str) -> None:
        """
        Unregister a tool from the registry
        
        Args:
            tool_name: Name of the tool to unregister
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Unregistered tool: {tool_name}")
    
    def get_tool(self, tool_name: str) -> Optional[ToolDefinition]:
        """
        Get a tool definition by name
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool definition or None if not found
        """
        return self.tools.get(tool_name)
    
    def get_all_tools(self) -> List[ToolDefinition]:
        """
        Get all tool definitions
        
        Returns:
            List of tool definitions
        """
        return list(self.tools.values())
    
    def get_tools_by_category(self, category: str) -> List[ToolDefinition]:
        """
        Get tools by category
        
        Args:
            category: Category to filter by
            
        Returns:
            List of tool definitions in the category
        """
        return [tool for tool in self.tools.values() if tool.category == category]
    
    def get_tools_by_tag(self, tag: str) -> List[ToolDefinition]:
        """
        Get tools by tag
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List of tool definitions with the tag
        """
        return [tool for tool in self.tools.values() if tag in tool.tags]
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """
        Execute a tool with the given parameters
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            context: Additional context for execution
            
        Returns:
            Tool execution result
        """
        # Get tool definition
        tool_def = self.get_tool(tool_name)
        if not tool_def:
            return ToolResult.error(f"Tool {tool_name} not found")
        
        # Check if handler is available
        if tool_def.handler is None:
            return ToolResult.error(f"Tool {tool_name} has no handler")
        
        # Validate parameters
        validation_result = self._validate_parameters(tool_def, parameters)
        if not validation_result["valid"]:
            return ToolResult.error(f"Parameter validation failed: {validation_result['error']}")
        
        # Process parameters (apply defaults, convert types)
        processed_params = validation_result["processed_params"]
        
        # Execute the tool
        execution_id = str(uuid.uuid4())
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Execute handler based on whether it's async
            if tool_def.is_async:
                result = await tool_def.handler(**processed_params)
            else:
                result = tool_def.handler(**processed_params)
            
            # Calculate execution time
            end_time = asyncio.get_event_loop().time()
            execution_time = end_time - start_time
            
            # Create result
            tool_result = ToolResult(
                result=result,
                success=True,
                execution_time=execution_time,
                metadata={
                    "execution_id": execution_id,
                    "tool_name": tool_name
                }
            )
            
            # Record execution
            self._record_execution(
                execution_id=execution_id,
                tool_name=tool_name,
                parameters=processed_params,
                result=tool_result,
                context=context
            )
            
            return tool_result
            
        except Exception as e:
            # Calculate execution time even for errors
            end_time = asyncio.get_event_loop().time()
            execution_time = end_time - start_time
            
            # Create error result
            error_result = ToolResult.error(
                error_message=str(e),
                metadata={
                    "execution_id": execution_id,
                    "tool_name": tool_name,
                    "error_type": type(e).__name__,
                    "execution_time": execution_time
                }
            )
            
            # Record execution
            self._record_execution(
                execution_id=execution_id,
                tool_name=tool_name,
                parameters=processed_params,
                result=error_result,
                context=context,
                error=str(e)
            )
            
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return error_result
    
    def _validate_parameters(self, tool_def: ToolDefinition, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate parameters against tool definition
        
        Args:
            tool_def: Tool definition
            parameters: Parameters to validate
            
        Returns:
            Validation result with processed parameters
        """
        processed_params = {}
        errors = []
        
        # Check for required parameters
        for param_name, param_def in tool_def.parameters.items():
            if param_def.required and param_name not in parameters:
                errors.append(f"Missing required parameter: {param_name}")
                continue
            
            # Get parameter value or default
            if param_name in parameters:
                value = parameters[param_name]
            elif param_def.default is not None:
                value = param_def.default
            else:
                # Skip optional parameters that weren't provided
                continue
            
            # Validate parameter type
            try:
                # Validate and convert value based on type
                if param_def.type == "string":
                    processed_params[param_name] = str(value)
                elif param_def.type == "integer":
                    processed_params[param_name] = int(value)
                elif param_def.type == "number":
                    processed_params[param_name] = float(value)
                elif param_def.type == "boolean":
                    if isinstance(value, str):
                        processed_params[param_name] = value.lower() in ["true", "1", "yes", "y"]
                    else:
                        processed_params[param_name] = bool(value)
                elif param_def.type == "array":
                    if not isinstance(value, list):
                        errors.append(f"Parameter {param_name} must be an array")
                    else:
                        processed_params[param_name] = value
                elif param_def.type == "object":
                    if not isinstance(value, dict):
                        errors.append(f"Parameter {param_name} must be an object")
                    else:
                        processed_params[param_name] = value
                else:
                    # Unknown type, just pass through
                    processed_params[param_name] = value
            except (ValueError, TypeError):
                errors.append(f"Invalid type for parameter {param_name}: expected {param_def.type}")
            
            # Validate enum values if specified
            if param_def.enum is not None and value not in param_def.enum:
                errors.append(f"Value for {param_name} must be one of: {', '.join(map(str, param_def.enum))}")
        
        if errors:
            return {
                "valid": False,
                "error": "; ".join(errors),
                "processed_params": processed_params
            }
        
        return {
            "valid": True,
            "processed_params": processed_params
        }
    
    def _record_execution(
        self,
        execution_id: str,
        tool_name: str,
        parameters: Dict[str, Any],
        result: ToolResult,
        context: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Record a tool execution
        
        Args:
            execution_id: ID of the execution
            tool_name: Name of the tool
            parameters: Parameters for the tool
            result: Execution result
            context: Additional context
            error: Error message (if any)
        """
        execution_record = {
            "execution_id": execution_id,
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result.to_dict(),
            "context_keys": list(context.keys()) if context else [],
            "timestamp": datetime.utcnow().isoformat(),
            "success": result.success
        }
        
        if error:
            execution_record["error"] = error
            
        # Limit the size of the executions list
        self.executions.append(execution_record)
        if len(self.executions) > 100:  # Keep only the last 100 executions
            self.executions = self.executions[-100:]
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the execution history
        
        Args:
            limit: Maximum number of executions to return
            
        Returns:
            List of execution records
        """
        return self.executions[-limit:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert registry to dictionary representation"""
        return {
            "tools": {name: tool.to_dict() for name, tool in self.tools.items()},
            "executions_count": len(self.executions)
        }

# Global registry instance
tool_registry = ToolRegistry()
