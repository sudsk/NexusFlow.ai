"""
Graph components for NexusFlow.ai

This package contains components for building and executing dynamic execution graphs:
- Builder: Creates execution graphs based on agent capabilities
- Router: Routes execution between nodes
- Execution: Executes flows with the graph engine
"""

from nexusflow.graph.builder import (
    DynamicGraph, 
    DynamicGraphBuilder,
    GraphNode, 
    GraphEdge
)

# These would be imported once implemented
# from nexusflow.graph.router import GraphRouter
# from nexusflow.graph.execution import GraphExecutionEngine

__all__ = [
    # Graph components
    'DynamicGraph',
    'DynamicGraphBuilder',
    'GraphNode',
    'GraphEdge',
    
    # These would be added once implemented
    # 'GraphRouter',
    # 'GraphExecutionEngine',
]
