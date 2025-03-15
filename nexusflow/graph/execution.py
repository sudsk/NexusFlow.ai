"""
Graph Execution Engine for NexusFlow.ai

This module provides the GraphExecutionEngine class, which handles the execution
of dynamic graphs in NexusFlow, orchestrating the flow between nodes.
"""

from typing import Dict, List, Any, Optional, Union, Callable, Set
import logging
import asyncio
import time
from datetime import datetime

from nexusflow.core.state import GraphState
from .builder import DynamicGraph, GraphNode
from .router import GraphRouter

logger = logging.getLogger(__name__)

class ExecutionResult:
    """Container for graph execution results"""
    
    def __init__(
        self,
        success: bool,
        output: Any,
        execution_path: List[str],
        execution_time: float,
        node_outputs: Dict[str, Any] = None,
        errors: Dict[str, str] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize execution result
        
        Args:
            success: Whether execution was successful
            output: Final output of the execution
            execution_path: Path of executed nodes (in order)
            execution_time: Total execution time in seconds
            node_outputs: Outputs from each node
            errors: Errors encountered during execution
            metadata: Additional metadata
        """
        self.success = success
        self.output = output
        self.execution_path = execution_path
        self.execution_time = execution_time
        self.node_outputs = node_outputs or {}
        self.errors = errors or {}
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary representation"""
        return {
            "success": self.success,
            "output": self.output,
            "execution_path": self.execution_path,
            "execution_time": self.execution_time,
            "node_outputs": self.node_outputs,
            "errors": self.errors,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }

class GraphExecutionEngine:
    """
    Engine for executing dynamic graphs
    
    The GraphExecutionEngine is responsible for orchestrating the execution
    of nodes in a dynamic graph, managing the flow of data between nodes,
    handling errors, and collecting results.
    """
    
    def __init__(
        self,
        graph: Optional[DynamicGraph] = None,
        router: Optional[GraphRouter] = None,
        max_steps: int = 100,
        timeout: Optional[float] = None
    ):
        """
        Initialize a graph execution engine
        
        Args:
            graph: The dynamic graph to execute (can be set later)
            router: The router to use (if None, a new one will be created)
            max_steps: Maximum number of execution steps
            timeout: Maximum execution time in seconds (None for no limit)
        """
        self.graph = graph
        self.router = router or GraphRouter(graph)
        self.max_steps = max_steps
        self.timeout = timeout
        
        # Execution state
        self.state = GraphState()
        self.execution_path = []
        self.node_outputs = {}
        self.errors = {}
    
    def set_graph(self, graph: DynamicGraph) -> None:
        """
        Set the graph for the engine
        
        Args:
            graph: The dynamic graph to execute
        """
        self.graph = graph
        self.router.set_graph(graph)
    
    async def execute(
        self,
        input_data: Any,
        start_node_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Execute the graph with the given input
        
        Args:
            input_data: Input data for the graph
            start_node_id: ID of the starting node (if None, use graph's start node)
            context: Additional context data for execution
            
        Returns:
            Execution result
        """
        if not self.graph:
            raise ValueError("No graph set for the execution engine")
        
        # Use graph's start node if not specified
        if start_node_id is None:
            if not self.graph.start_node_id:
                raise ValueError("No start node specified for the graph")
            start_node_id = self.graph.start_node_id
        
        # Reset execution state
        self.state = GraphState()
        self.execution_path = []
        self.node_outputs = {}
        self.errors = {}
        
        # Initialize context
        context = context or {}
        
        # Set start time
        start_time = time.time()
        
        # Initialize with starting input
        current_input = input_data
        steps = 0
        final_output = None
        
        try:
            # Execute until max steps, timeout, or completion
            while steps < self.max_steps:
                # Check timeout
                if self.timeout and (time.time() - start_time) > self.timeout:
                    logger.warning(f"Execution timed out after {self.timeout} seconds")
                    raise TimeoutError(f"Execution timed out after {self.timeout} seconds")
                
                steps += 1
                
                # Get current node
                current_node_id = self._get_current_node_id(steps)
                if not current_node_id:
                    break
                
                current_node = self.graph.nodes.get(current_node_id)
                if not current_node:
                    raise ValueError(f"Node {current_node_id} not found in graph")
                
                # Update execution path
                self.execution_path.append(current_node_id)
                
                # Update state
                self.state.set_current_node(current_node_id)
                node_state = self.state.get_node_state(current_node_id)
                if node_state:
                    node_state.add_input(current_input)
                
                # Execute node
                try:
                    logger.info(f"Executing node {current_node_id} (step {steps})")
                    node_output = await self._execute_node(current_node, current_input, context)
                    
                    # Save output
                    self.node_outputs[current_node_id] = node_output
                    
                    # Update node state
                    if node_state:
                        node_state.add_output(node_output)
                    
                    # Check if this is the end node
                    if current_node_id == self.graph.end_node_id:
                        final_output = node_output
                        logger.info(f"Reached end node {current_node_id}, execution complete")
                        break
                    
                    # Determine next nodes
                    next_node_ids = await self.router.get_next_nodes(current_node_id, node_output, self.state)
                    
                    if not next_node_ids:
                        logger.info(f"No next nodes from {current_node_id}, execution complete")
                        final_output = node_output  # Use this as final output if no more nodes
                        break
                    
                    # For simplicity, just take the first next node
                    # In a more complex implementation, we might handle parallel execution
                    next_node_id = next_node_ids[0]
                    
                    # Prepare input for next node
                    current_input = node_output
                    
                except Exception as e:
                    logger.error(f"Error executing node {current_node_id}: {str(e)}")
                    self.errors[current_node_id] = str(e)
                    
                    # Try to continue with next nodes if possible
                    try:
                        next_node_ids = await self.router.get_next_nodes(current_node_id, None, self.state)
                        if not next_node_ids:
                            logger.error(f"Cannot continue after error in node {current_node_id}")
                            raise
                        
                        next_node_id = next_node_ids[0]
                        current_input = {"error": str(e), "original_input": current_input}
                        
                    except Exception:
                        logger.error(f"Execution failed at node {current_node_id}")
                        raise
            
            # Check if max steps reached
            if steps >= self.max_steps:
                logger.warning(f"Execution reached maximum steps ({self.max_steps})")
                
                # Use the last node's output as final output
                last_node_id = self.execution_path[-1] if self.execution_path else None
                if last_node_id:
                    final_output = self.node_outputs.get(last_node_id)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Create success result
            return ExecutionResult(
                success=True,
                output=final_output,
                execution_path=self.execution_path,
                execution_time=execution_time,
                node_outputs=self.node_outputs,
                errors=self.errors,
                metadata={
                    "steps": steps,
                    "max_steps_reached": steps >= self.max_steps
                }
            )
            
        except Exception as e:
            logger.exception(f"Graph execution failed: {str(e)}")
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Create error result
            return ExecutionResult(
                success=False,
                output=None,
                execution_path=self.execution_path,
                execution_time=execution_time,
                node_outputs=self.node_outputs,
                errors=self.errors,
                metadata={
                    "steps": steps,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
    
    async def _execute_node(
        self,
        node: GraphNode,
        input_data: Any,
        context: Dict[str, Any]
    ) -> Any:
        """
        Execute a single node
        
        Args:
            node: The node to execute
            input_data: Input data for the node
            context: Additional context data
            
        Returns:
            Node execution output
        """
        # Check if node has a handler
        if not node.handler:
            logger.warning(f"Node {node.node_id} has no handler, passing input through")
            return input_data
        
        # Build execution context
        node_context = {
            **context,
            "node_id": node.node_id,
            "node_type": node.node_type,
            "execution_path": self.execution_path.copy(),
            "state": self.state
        }
        
        # Call the node handler
        if asyncio.iscoroutinefunction(node.handler):
            # Async handler
            return await node.handler(input_data, node_context)
        else:
            # Sync handler
            return node.handler(input_data, node_context)
    
    def _get_current_node_id(self, step: int) -> Optional[str]:
        """
        Get the ID of the current node to execute
        
        Args:
            step: Current execution step
            
        Returns:
            ID of the current node, or None if execution is complete
        """
        if step == 1:
            # First step, use start node
            return self.graph.start_node_id
        
        # Check if we have a current node in state
        if self.state.current_node_id:
            return self.state.current_node_id
        
        # No current node, execution is complete
        return None
    
    def get_execution_status(self) -> Dict[str, Any]:
        """
        Get the current execution status
        
        Returns:
            Dictionary with execution status information
        """
        return {
            "execution_path": self.execution_path,
            "current_node": self.state.current_node_id,
            "completed_nodes": list(self.node_outputs.keys()),
            "errors": self.errors,
            "state": self.state.to_dict()
        }
    
    def visualize_execution(self) -> Dict[str, Any]:
        """
        Generate visualization data for the execution
        
        Returns:
            Visualization data
        """
        if not self.graph:
            return {"error": "No graph set for visualization"}
        
        # Build node data
        nodes = []
        for node_id, node in self.graph.nodes.items():
            executed = node_id in self.execution_path
            has_error = node_id in self.errors
            
            nodes.append({
                "id": node_id,
                "type": node.node_type,
                "executed": executed,
                "error": has_error,
                "position": 0  # Would need layout algorithm for actual visualization
            })
        
        # Build edge data
        edges = []
        for edge in self.graph.edges:
            source_executed = edge.source_id in self.execution_path
            target_executed = edge.target_id in self.execution_path
            traversed = (source_executed and target_executed and 
                        self.execution_path.index(edge.source_id) < self.execution_path.index(edge.target_id))
            
            edges.append({
                "source": edge.source_id,
                "target": edge.target_id,
                "traversed": traversed
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "execution_path": self.execution_path,
            "errors": self.errors
        }
