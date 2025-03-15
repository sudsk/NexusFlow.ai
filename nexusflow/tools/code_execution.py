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
import time
import re

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
                    "description": "Maximum execution time in seconds",
                    "required": False,
                    "default": self.timeout
                },
                "language": {
                    "type": "string",
                    "description": "Programming language of the code",
                    "required": False,
                    "default": "python",
                    "enum": ["python", "javascript"]
                }
            },
            handler=self.execute_code,
            is_async=True,
            category="development",
            tags=["code", "execution", "sandbox"]
        )
        
        tool_registry.register_tool(tool_def)
    
    async def execute_code(
        self,
        code: str,
        timeout: Optional[int] = None,
        language: str = "python"
    ) -> Dict[str, Any]:
        """
        Execute code in a sandbox environment
        
        Args:
            code: Code to execute
            timeout: Maximum execution time in seconds
            language: Programming language of the code
            
        Returns:
            Execution results
        """
        # Use default timeout if not provided
        timeout = timeout or self.timeout
        
        # Check language
        if language.lower() != "python":
            return {
                "error": f"Language '{language}' is not supported. Only Python is currently supported.",
                "output": "",
                "execution_time": 0
            }
        
        # Check and preprocess code
        sanitized_code = self._sanitize_code(code)
        if isinstance(sanitized_code, dict) and "error" in sanitized_code:
            return sanitized_code
        
        # Execute code
        try:
            # Prepare for execution
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Measure execution time
            start_time = time.time()
            
            # Create execution task
            execution_task = asyncio.create_task(
                self._execute_python_code(sanitized_code, stdout_capture, stderr_capture)
            )
            
            # Wait for execution with timeout
            try:
                result = await asyncio.wait_for(execution_task, timeout=timeout)
                execution_time = time.time() - start_time
                
                # Get captured output
                stdout_output = stdout_capture.getvalue()
                stderr_output = stderr_capture.getvalue()
                
                # Truncate output if too large
                if len(stdout_output) > self.max_output_size:
                    stdout_output = stdout_output[:self.max_output_size] + "\n... [output truncated]"
                
                if len(stderr_output) > self.max_output_size:
                    stderr_output = stderr_output[:self.max_output_size] + "\n... [error output truncated]"
                
                return {
                    "result": result,
                    "stdout": stdout_output,
                    "stderr": stderr_output,
                    "execution_time": execution_time
                }
                
            except asyncio.TimeoutError:
                # Cancel the task if it's still running
                execution_task.cancel()
                try:
                    await execution_task
                except asyncio.CancelledError:
                    pass
                
                return {
                    "error": f"Execution timed out after {timeout} seconds",
                    "stdout": stdout_capture.getvalue(),
                    "stderr": stderr_capture.getvalue(),
                    "execution_time": timeout
                }
                
        except Exception as e:
            logger.exception(f"Error executing code: {str(e)}")
            return {
                "error": f"Error executing code: {str(e)}",
                "traceback": traceback.format_exc(),
                "execution_time": 0
            }
    
    async def _execute_python_code(
        self,
        code: str,
        stdout_capture: io.StringIO,
        stderr_capture: io.StringIO
    ) -> Any:
        """
        Execute Python code and capture output
        
        Args:
            code: Python code to execute
            stdout_capture: StringIO to capture stdout
            stderr_capture: StringIO to capture stderr
            
        Returns:
            Result of the code execution
        """
        # Define a restricted globals dictionary
        restricted_globals = {
            "__builtins__": {
                name: getattr(__builtins__, name)
                for name in dir(__builtins__)
                if name not in [
                    "open", "eval", "exec", "compile", 
                    "__import__", "input", "memoryview",
                    "breakpoint", "globals", "locals"
                ]
            }
        }
        
        # Add safe imports if allowed
        if self.allow_imports:
            restricted_globals["__import__"] = self._restricted_import
        
        # Create local variables dictionary
        local_vars = {}
        
        # Redirect stdout and stderr
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            try:
                # Compile the code
                compiled_code = compile(code, "<string>", "exec")
                
                # Execute the code
                exec(compiled_code, restricted_globals, local_vars)
                
                # Check for result variable
                if "result" in local_vars:
                    return local_vars["result"]
                else:
                    # Return all local variables as the result
                    return {k: v for k, v in local_vars.items() if not k.startswith("__")}
                
            except Exception as e:
                # Capture the exception and traceback
                stderr_capture.write(f"Exception: {str(e)}\n")
                stderr_capture.write(traceback.format_exc())
                raise
    
    def _restricted_import(self, name: str, *args, **kwargs):
        """
        Restricted import function to enforce module restrictions
        
        Args:
            name: Name of the module to import
            *args: Additional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Imported module
            
        Raises:
            ImportError: If the module is disallowed
        """
        # Check if imports are allowed
        if not self.allow_imports:
            raise ImportError(f"Imports are not allowed in this sandbox")
        
        # Check if the module is explicitly disallowed
        if any(name.startswith(module) for module in self.disallowed_modules):
            raise ImportError(f"Module '{name}' is not allowed in this sandbox")
        
        # Check if the module is in the allowed list (if specified)
        if self.allowed_modules and not any(name.startswith(module) for module in self.allowed_modules):
            raise ImportError(f"Module '{name}' is not in the allowed modules list")
        
        # Import the module
        return __import__(name, *args, **kwargs)
    
    def _sanitize_code(self, code: str) -> Union[str, Dict[str, str]]:
        """
        Sanitize code to ensure it's safe to execute
        
        Args:
            code: Code to sanitize
            
        Returns:
            Sanitized code or error dictionary
        """
        # Check for potentially dangerous imports
        for module in self.disallowed_modules:
            import_patterns = [
                rf"import\s+{module}(\s|$|\.|,)",
                rf"from\s+{module}\s+import",
                rf"__import__\s*\(\s*['\"]({module})['\"]",
            ]
            
            for pattern in import_patterns:
                if re.search(pattern, code):
                    return {
                        "error": f"Disallowed module import: '{module}'",
                        "output": "",
                        "execution_time": 0
                    }
        
        # Check for potentially dangerous calls
        dangerous_functions = [
            r"eval\s*\(", r"exec\s*\(", r"compile\s*\(",
            r"__import__\s*\(", r"globals\s*\(", r"locals\s*\(",
            r"getattr\s*\(.*,\s*['\"]__.*__",  # Accessing dunder attributes
            r"open\s*\("
        ]
        
        for func in dangerous_functions:
            if re.search(func, code):
                return {
                    "error": f"Disallowed function call detected: '{func.replace('\\s*\\(', '')}'",
                    "output": "",
                    "execution_time": 0
                }
        
        return code

# Create a global instance
code_execution_tool = CodeExecutionTool()

# Export the tool
__all__ = ["CodeExecutionTool", "code_execution_tool"]
