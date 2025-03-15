"""
Code Execution Tool for NexusFlow.ai

This module provides a tool for executing code in a secure sandbox environment.
"""

import logging
import asyncio
import traceback
import io
import sys
import contextlib
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json

from .registry import ToolDefinition, ToolResult, tool_registry

logger = logging.getLogger(__name__)

class CodeExecutionTool:
    """Tool for executing code in a sandbox environment"""
    
    def __init__(
        self,
        timeout: int = 5,
        max_output_size: int = 10000,
        allow_imports: bool = True,
        allowed_modules: Optional[List[str]] = None,
        disallowed_modules: Optional[List[str]] = None
    ):
        """
        Initialize a code execution tool
        
        Args:
            timeout: Maximum execution time in seconds
            max_output_size: Maximum output size in characters
            allow_imports: Whether to allow imports
            allowed_modules: List of allowed modules (if None, all modules are allowed except disallowed_modules)
            disallowed_modules: List of disallowed modules
        """
        self.timeout = timeout
        self.max_output_size = max_output_size
        self.allow_imports = allow_imports
        self.allowed_modules = allowed_modules
        self.disallowed_modules = disallowed_modules or [
            "os", "subprocess", "sys", "builtins", "importlib", 
            "ctypes", "threading", "socket", "asyncio.subprocess",
            "multiprocessing", "pwd", "grp", "pty", "shutil", "requests"
        ]
        
        # Register the tool
        self._register_tool()
    
    def _register_tool(self):
        """Register the code execution tool with the registry"""
        tool_def = ToolDefinition(
            name="code_execution",
            description="Execute Python code in a secure sandbox environment",
            parameters={
                "code": {
                    "type": "string",
                    "description": "Python code to execute"
                },
                "timeout": {
                    "type": "integer",
