"""
Tools for NexusFlow.ai

This package contains tools that agents can use:
- Registry: Central registry for all tools
- Web Search: Search the web for information
- Code Execution: Execute code in a sandbox environment
- Data Analysis: Analyze data and generate insights
"""

from nexusflow.tools.registry import ToolRegistry, ToolDefinition, ToolResult, tool_registry
from nexusflow.tools.web_search import WebSearchTool, web_search_tool
from nexusflow.tools.code_execution import CodeExecutionTool, code_execution_tool
from nexusflow.tools.data_analysis import DataAnalysisTool, data_analysis_tool

__all__ = [
    # Tool registry
    'ToolRegistry',
    'ToolDefinition',
    'ToolResult',
    'tool_registry',
    
    # Web search tool
    'WebSearchTool',
    'web_search_tool',
    
    # Code execution tool
    'CodeExecutionTool',
    'code_execution_tool',
    
    # Data analysis tool
    'DataAnalysisTool',
    'data_analysis_tool',
]
