# backend/services/tool/registry_service.py
from typing import Dict, List, Any, Optional, Union, Callable
import logging
import importlib
import inspect
import json
import os
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Service for registering and executing tools across frameworks"""
    
    def __init__(self):
        self._tools = {}  # Dictionary of registered tools by name
        self._functions = {}  # Dictionary of tool functions by name
        self._register_default_tools()
        
    def _register_default_tools(self):
        """Register built-in tools"""
        try:
            # Import default tools module
            from ...tools.default_tools import (
                web_search,
                calculate,
                data_analysis,
                document_retrieval,
                code_execution,
                translation
            )
            
            # Register tool functions
            self.register_function("web_search", web_search)
            self.register_function("calculate", calculate)
            self.register_function("data_analysis", data_analysis)
            self.register_function("document_retrieval", document_retrieval)
            self.register_function("code_execution", code_execution)
            self.register_function("translation", translation)
            
            # Register tool metadata
            self.register_tool({
                "name": "web_search",
                "description": "Search the web for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                },
                "function_name": "web_search",
                "is_enabled": True,
                "metadata": {
                    "category": "information_retrieval",
                    "compatible_frameworks": ["langgraph", "crewai", "autogen", "dspy"]
                }
            })
            
            self.register_tool({
                "name": "calculate",
                "description": "Perform calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "The mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                },
                "function_name": "calculate",
                "is_enabled": True,
                "metadata": {
                    "category": "utility",
                    "compatible_frameworks": ["langgraph", "crewai", "autogen", "dspy"]
                }
            })
            
            self.register_tool({
                "name": "data_analysis",
                "description": "Analyze data and generate insights",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "array",
                            "description": "Data to analyze"
                        },
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis to perform",
                            "enum": ["descriptive", "exploratory"],
                            "default": "descriptive"
                        }
                    },
                    "required": ["data"]
                },
                "function_name": "data_analysis",
                "is_enabled": True,
                "metadata": {
                    "category": "data_processing",
                    "compatible_frameworks": ["langgraph", "crewai", "autogen"]
                }
            })
            
            self.register_tool({
                "name": "document_retrieval",
                "description": "Retrieve documents from a knowledge base",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for documents"
                        },
                        "collection": {
                            "type": "string",
                            "description": "Collection to search",
                            "default": "default"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of documents to return",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                },
                "function_name": "document_retrieval",
                "is_enabled": True,
                "metadata": {
                    "category": "information_retrieval",
                    "compatible_frameworks": ["langgraph", "crewai", "autogen", "dspy"]
                }
            })
            
            self.register_tool({
                "name": "code_execution",
                "description": "Execute code in a secure sandbox environment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "language": {
                            "type": "string",
                            "description": "Programming language",
                            "enum": ["python", "javascript"]
                        },
                        "code": {
                            "type": "string",
                            "description": "Code to execute"
                        }
                    },
                    "required": ["language", "code"]
                },
                "function_name": "code_execution",
                "is_enabled": True,
                "metadata": {
                    "category": "development",
                    "compatible_frameworks": ["langgraph", "crewai", "autogen"]
                }
            })
            
            self.register_tool({
                "name": "translation",
                "description": "Translate text from one language to another",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text to translate"
                        },
                        "source_language": {
                            "type": "string",
                            "description": "Source language code",
                            "default": "auto"
                        },
                        "target_language": {
                            "type": "string",
                            "description": "Target language code"
                        }
                    },
                    "required": ["text", "target_language"]
                },
                "function_name": "translation",
                "is_enabled": True,
                "metadata": {
                    "category": "language",
                    "compatible_frameworks": ["langgraph", "crewai", "autogen", "dspy"]
                }
            })
            
            logger.info("Successfully registered default tools")
        except ImportError as e:
            logger.warning(f"Failed to import default tools: {str(e)}")
        except Exception as e:
            logger.exception(f"Error registering default tools: {str(e)}")
    
    def register_tool(self, tool_data: Dict[str, Any]) -> bool:
        """
        Register a tool in the registry
        
        Args:
            tool_data: Tool configuration
            
        Returns:
            Success status
        """
        tool_name = tool_data.get("name")
        if not tool_name:
            logger.error("Cannot register tool without a name")
            return False
        
        # Store tool configuration
        self._tools[tool_name] = tool_data
        
        # Log successful registration
        logger.info(f"Registered tool: {tool_name}")
        return True
    
    def register_function(self, tool_name: str, function: Callable) -> bool:
        """
        Register a function for a tool
        
        Args:
            tool_name: Name of the tool
            function: Function to register
            
        Returns:
            Success status
        """
        if not callable(function):
            logger.error(f"Cannot register non-callable object as tool function for {tool_name}")
            return False
        
        self._functions[tool_name] = function
        logger.info(f"Registered function for tool: {tool_name}")
        return True
    
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
        func = self._functions.get(tool_name)
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
                # Execute regular function (wrap in asyncio task)
                if context is not None:
                    result = await asyncio.to_thread(func, parameters, context=context)
                else:
                    result = await asyncio.to_thread(func, parameters)
                    
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
            {**config, "has_implementation": config.get("name") in self._functions}
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
            "has_implementation": tool_name in self._functions
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
            {**config, "has_implementation": config.get("name") in self._functions}
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
    
    def get_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get tools by category
        
        Args:
            category: Tool category
            
        Returns:
            List of tool configurations
        """
        return [
            {**config, "has_implementation": config.get("name") in self._functions}
            for config in self._tools.values()
            if config.get("metadata", {}).get("category") == category
        ]
    
    def get_disabled_tools(self) -> List[Dict[str, Any]]:
        """
        Get all disabled tools
        
        Returns:
            List of disabled tool configurations
        """
        return [
            {**config, "has_implementation": config.get("name") in self._functions}
            for config in self._tools.values()
            if not config.get("is_enabled", True)
        ]


# Singleton instance
_tool_registry = None

def get_tool_registry() -> ToolRegistry:
    """
    Get the global tool registry instance
    
    Returns:
        ToolRegistry instance
    """
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry
