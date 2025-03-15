"""
Graph Router for NexusFlow.ai

This module provides the GraphRouter class, which handles routing decisions
within a dynamic execution graph based on node outputs and edge conditions.
"""

from typing import Dict, List, Any, Optional, Union, Callable, Awaitable
import logging
import asyncio

from nexusflow.core.state import GraphState
from .builder import DynamicGraph, GraphNode, GraphEdge

logger = logging.getLogger(__name__)

class GraphRouter:
    """
    Router for determining execution paths within a dynamic execution graph
    
    The GraphRouter is responsible for making routing decisions about which
    nodes should be executed next based on the outputs of previous nodes and
    the conditions defined on edges.
    """
    
    def __init__(self, graph: Optional[DynamicGraph] = None):
        """
        Initialize a graph router
        
        Args:
            graph: The dynamic graph to route (can be set later)
        """
        self.graph = graph
    
    def set_graph(self, graph: DynamicGraph) -> None:
        """
        Set the graph for the router
        
        Args:
            graph: The dynamic graph to route
        """
        self.graph = graph
    
    async def get_next_nodes(
        self, 
        current_node_id: str, 
        output: Any, 
        state: GraphState
    ) -> List[str]:
        """
        Determine the next nodes to execute based on output and state
        
        Args:
            current_node_id: ID of the current node
            output: Output from the current node
            state: Current graph state
            
        Returns:
            List of node IDs to execute next
        """
        if not self.graph:
            raise ValueError("No graph set for the router")
        
        # Find all outgoing edges from the current node
        outgoing_edges = [
            edge for edge in self.graph.edges
            if edge.source_id == current_node_id
        ]
        
        if not outgoing_edges:
            # No outgoing edges, execution stops at this node
            return []
        
        # Evaluate conditions on each edge to determine which ones to follow
        valid_edges = []
        
        for edge in outgoing_edges:
            is_valid = await self._evaluate_edge_condition(edge, output, state)
            if is_valid:
                valid_edges.append(edge)
        
        # If there are conditional edges and none match, check for a default edge
        if not valid_edges and any(edge.condition is not None for edge in outgoing_edges):
            default_edge = next(
                (edge for edge in outgoing_edges if edge.condition is None),
                None
            )
            if default_edge:
                valid_edges.append(default_edge)
        
        # If no edges are valid (and no default), return empty list
        if not valid_edges:
            return []
        
        # Return the target nodes of valid edges
        return [edge.target_id for edge in valid_edges]
    
    async def _evaluate_edge_condition(
        self, 
        edge: GraphEdge, 
        output: Any, 
        state: GraphState
    ) -> bool:
        """
        Evaluate the condition of an edge
        
        Args:
            edge: The edge to evaluate
            output: Output from the source node
            state: Current graph state
            
        Returns:
            True if the condition is met, False otherwise
        """
        # If no condition is specified, the edge is always valid
        if not edge.condition:
            return True
        
        try:
            # Call the condition function
            if asyncio.iscoroutinefunction(edge.condition):
                # Async condition
                result = await edge.condition(output, state)
            else:
                # Sync condition
                result = edge.condition(output, state)
            
            return bool(result)
        except Exception as e:
            logger.error(f"Error evaluating edge condition from {edge.source_id} to {edge.target_id}: {str(e)}")
            return False
    
    async def get_all_possible_paths(
        self, 
        start_node_id: str, 
        state: GraphState
    ) -> List[List[str]]:
        """
        Get all possible execution paths from a starting node
        
        This is primarily used for visualization and debugging.
        
        Args:
            start_node_id: ID of the starting node
            state: Current graph state
            
        Returns:
            List of possible paths (each path is a list of node IDs)
        """
        if not self.graph:
            raise ValueError("No graph set for the router")
        
        paths = []
        await self._find_paths(start_node_id, [], paths, set(), state)
        return paths
    
    async def _find_paths(
        self, 
        current_node_id: str, 
        current_path: List[str],
        all_paths: List[List[str]],
        visited: Set[str],
        state: GraphState
    ) -> None:
        """
        Recursively find all paths from the current node
        
        Args:
            current_node_id: ID of the current node
            current_path: Path built so far
            all_paths: List to store all found paths
            visited: Set of already visited nodes (to avoid cycles)
            state: Current graph state
        """
        # Add current node to the path
        path = current_path + [current_node_id]
        
        # If we've already visited this node, stop to avoid cycles
        if current_node_id in visited:
            all_paths.append(path)
            return
        
        # Mark current node as visited
        visited.add(current_node_id)
        
        # Find all outgoing edges
        outgoing_edges = [
            edge for edge in self.graph.edges
            if edge.source_id == current_node_id
        ]
        
        if not outgoing_edges:
            # No outgoing edges, add the path to the result
            all_paths.append(path)
            return
        
        # Recursively explore each outgoing edge
        for edge in outgoing_edges:
            # Skip edges that would lead to cycles
            if edge.target_id not in visited:
                await self._find_paths(
                    edge.target_id,
                    path,
                    all_paths,
                    visited.copy(),  # Create a copy to avoid cross-path interference
                    state
                )
    
    def get_node_dependencies(self, node_id: str) -> List[str]:
        """
        Get the IDs of nodes that the specified node depends on
        
        Args:
            node_id: ID of the node
            
        Returns:
            List of node IDs that the specified node depends on
        """
        if not self.graph:
            raise ValueError("No graph set for the router")
        
        # Find all incoming edges to the node
        incoming_edges = [
            edge for edge in self.graph.edges
            if edge.target_id == node_id
        ]
        
        # Return the source nodes of incoming edges
        return [edge.source_id for edge in incoming_edges]
    
    def get_dependent_nodes(self, node_id: str) -> List[str]:
        """
        Get the IDs of nodes that depend on the specified node
        
        Args:
            node_id: ID of the node
            
        Returns:
            List of node IDs that depend on the specified node
        """
        if not self.graph:
            raise ValueError("No graph set for the router")
        
        # Find all outgoing edges from the node
        outgoing_edges = [
            edge for edge in self.graph.edges
            if edge.source_id == node_id
        ]
        
        # Return the target nodes of outgoing edges
        return [edge.target_id for edge in outgoing_edges]
