# backend/services/tool/tool_registry.py
"""
Tool Registry service for managing and executing tools
"""
import logging
import importlib
import inspect
import asyncio
from typing import Dict, List, Any, Optional, Callable, Awaitable, Union

logger = logging.getLogger(__name__)

class ToolRegistry:
    """
    Registry for managing and executing tools available to agents
    """
    
    def __init__(self):
        self._tools = {}
        self._function_registry = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools that come with NexusFlow"""
        try:
            # Import the default tools module
            from ...tools.default_tools import (
                web_search, 
                calculate, 
                data_analysis,
                document_retrieval,
                code_execution,
                translation
            )
            
            # Register each tool
            self.register_tool_function("web_search", web_search)
            self.register_tool_function("calculate", calculate)
            self.register_tool_function("data_analysis", data_analysis)
            self.register_tool_function("document_retrieval", document_retrieval)
            self.register_tool_function("code_execution", code_execution)
            self.register_tool_function("translation", translation)
            
            logger.info("Default tools registered successfully")
        except ImportError as e:
            logger.warning(f"Could not import default tools: {str(e)}")
        except Exception as e:
            logger.error(f"Error registering default tools: {str(e)}")
    
    def register_tool(self, tool_config: Dict[str, Any]) -> bool:
        """
        Register a tool in the registry
        
        Args:
            tool_config: Tool configuration
            
        Returns:
            Success status
        """
        tool_name = tool_config.get("name")
        if not tool_name:
            logger.error("Cannot register tool without a name")
            return False
        
        # Store tool configuration
        self._tools[tool_name] = tool_config
        
        # Try to load the function if function_name is provided
        function_name = tool_config.get("function_name")
        if function_name:
            try:
                self._load_function(tool_name, function_name)
            except Exception as e:
                logger.warning(f"Failed to load function for tool {tool_name}: {str(e)}")
                # We still register the tool even if function loading fails
                # It might be loaded later or handled separately
        
        logger.info(f"Tool '{tool_name}' registered successfully")
        return True
    
    def register_tool_function(self, tool_name: str, func: Callable) -> bool:
        """
        Register a function for a tool
        
        Args:
            tool_name: Name of the tool
            func: Function to register
            
        Returns:
            Success status
        """
        if not callable(func):
            logger.error(f"Cannot register non-callable object as tool function for {tool_name}")
            return False
        
        self._function_registry[tool_name] = func
        logger.info(f"Function registered for tool '{tool_name}'")
        return True
    
    def _load_function(self, tool_name: str, function_path: str) -> bool:
        """
        Load a function for a tool
        
        Args:
            tool_name: Name of the tool
            function_path: Path to the function (module.function or just function)
            
        Returns:
            Success status
        """
        try:
            if '.' in function_path:
                # Import from specified module
                module_name, function_name = function_path.rsplit('.', 1)
                module = importlib.import_module(module_name)
                func = getattr(module, function_name)
            else:
                # Check built-in tools first
                try:
                    from ...tools.default_tools import default_tools
                    if hasattr(default_tools, function_path):
                        func = getattr(default_tools, function_path)
                    else:
                        raise AttributeError(f"Function {function_path} not found in default_tools")
                except (ImportError, AttributeError):
                    # Try importing from default tools module directly
                    from ...tools import default_tools
                    func = getattr(default_tools, function_path)
            
            # Register the function
            return self.register_tool_function(tool_name, func)
            
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load function {function_path} for tool {tool_name}: {str(e)}")
            return False
    
    async def execute_tool(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool with the given parameters
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            context: Additional context for execution
            
        Returns:
            Execution result
        """
        # Check if tool exists
        if tool_name not in self._tools:
            logger.error(f"Tool '{tool_name}' not found in registry")
            return {
                "error": f"Tool '{tool_name}' not found",
                "status": "error"
            }
        
        # Get tool configuration
        tool_config = self._tools[tool_name]
        
        # Check if tool is enabled
        if not tool_config.get("is_enabled", True):
            logger.warning(f"Attempted to execute disabled tool '{tool_name}'")
            return {
                "error": f"Tool '{tool_name}' is disabled",
                "status": "error"
            }
        
        # Check if function is available
        func = self._function_registry.get(tool_name)
        if not func:
            logger.error(f"No function available for tool '{tool_name}'")
            return {
                "error": f"Tool '{tool_name}' has no implementation",
                "status": "error"
            }
        
        # Execute the function
        try:
            start_time = datetime.now()
            
            # Check if function is async
            if inspect.iscoroutinefunction(func):
                # Execute async function
                if context is not None:
                    result = await func(parameters, context=context)
                else:
                    result = await func(parameters)
            else:
                # Execute regular function
                if context is not None:
                    result = func(parameters, context=context)
                else:
                    result = func(parameters)
                    
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Format the result
            return {
                "result": result,
                "tool": tool_name,
                "execution_time": execution_time,
                "status": "success"
            }
            
        except Exception as e:
            logger.exception(f"Error executing tool '{tool_name}': {str(e)}")
            return {
                "error": str(e),
                "tool": tool_name,
                "status": "error"
            }
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """
        Get all registered tools
        
        Returns:
            List of tool configurations
        """
        return [
            {**config, "has_implementation": config.get("name") in self._function_registry}
            for config in self._tools.values()
        ]
    
    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific tool by name
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool configuration or None if not found
        """
        if tool_name not in self._tools:
            return None
            
        config = self._tools[tool_name]
        return {
            **config, 
            "has_implementation": tool_name in self._function_registry
        }
    
    def get_tools_for_framework(self, framework: str) -> List[Dict[str, Any]]:
        """
        Get tools compatible with a specific framework
        
        Args:
            framework: Framework name
            
        Returns:
            List of compatible tool configurations
        """
        return [
            {**config, "has_implementation": config.get("name") in self._function_registry}
            for config in self._tools.values()
            if self._is_tool_compatible_with_framework(config, framework)
        ]
    
    def _is_tool_compatible_with_framework(self, tool_config: Dict[str, Any], framework: str) -> bool:
        """
        Check if a tool is compatible with a framework
        
        Args:
            tool_config: Tool configuration
            framework: Framework name
            
        Returns:
            True if compatible, False otherwise
        """
        # If tool has no specific framework compatibility, assume it's compatible with all
        if not tool_config.get("metadata", {}).get("compatible_frameworks"):
            return True
            
        # Check if framework is in the compatible_frameworks list
        return framework in tool_config.get("metadata", {}).get("compatible_frameworks", [])

# Singleton instance
_tool_registry = None

def get_tool_registry() -> ToolRegistry:
    """
    Get the global tool registry
    
    Returns:
        ToolRegistry instance
    """
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry
