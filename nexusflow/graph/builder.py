"""
Dynamic graph builder for NexusFlow.ai

This module provides the DynamicGraphBuilder class, which builds execution
graphs based on agent capabilities and relationships.
"""

from typing import Dict, List, Any, Optional, Set, Union, Callable
import logging
import uuid
from datetime import datetime

from nexusflow.core.agent import Agent
from nexusflow.core.capability import capability_registry, CapabilityType
from nexusflow.core.state import GraphState

logger = logging.getLogger(__name__)

class GraphNode:
    """Node in an execution graph"""
    
    def __init__(
        self,
        node_id: str,
        node_type: str,
        agent: Optional[Agent] = None,
        handler: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a graph node
        
        Args:
            node_id: ID of the node
            node_type: Type of the node
            agent: Associated agent (if any)
            handler: Function to handle node execution
            metadata: Additional metadata
        """
        self.node_id = node_id
        self.node_type = node_type
        self.agent = agent
        self.handler = handler
        self.metadata = metadata or {}
        self.inputs = []
        self.outputs = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "agent_id": self.agent.agent_id if self.agent else None,
            "agent_name": self.agent.name if self.agent else None,
            "metadata": self.metadata
        }


class GraphEdge:
    """Edge in an execution graph"""
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        edge_type: str = "default",
        condition: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a graph edge
        
        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            edge_type: Type of the edge
            condition: Function to determine if the edge should be followed
            metadata: Additional metadata
        """
        self.source_id = source_id
        self.target_id = target_id
        self.edge_type = edge_type
        self.condition = condition
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary representation"""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type,
            "metadata": self.metadata
        }


class DynamicGraph:
    """Dynamic execution graph"""
    
    def __init__(self, graph_id: Optional[str] = None):
        """
        Initialize a dynamic graph
        
        Args:
            graph_id: ID of the graph (generated if not provided)
        """
        self.graph_id = graph_id or str(uuid.uuid4())
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.start_node_id: Optional[str] = None
        self.end_node_id: Optional[str] = None
        self.state = GraphState()
    
    def add_node(self, node: GraphNode) -> str:
        """
        Add a node to the graph
        
        Args:
            node: Node to add
            
        Returns:
            ID of the added node
        """
        self.nodes[node.node_id] = node
        self.state.add_node(node.node_id, node.node_type)
        return node.node_id
    
    def add_edge(self, edge: GraphEdge) -> None:
        """
        Add an edge to the graph
        
        Args:
            edge: Edge to add
        """
        self.edges.append(edge)
        self.state.add_edge(edge.source_id, edge.target_id, edge.edge_type)
    
    def set_start_node(self, node_id: str) -> None:
        """
        Set the start node of the graph
        
        Args:
            node_id: ID of the start node
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found in graph")
        self.start_node_id = node_id
    
    def set_end_node(self, node_id: str) -> None:
        """
        Set the end node of the graph
        
        Args:
            node_id: ID of the end node
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found in graph")
        self.end_node_id = node_id
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the graph with the given input
        
        Args:
            input_data: Input data for the graph
            
        Returns:
            Results of the graph execution
        """
        if not self.start_node_id:
            raise ValueError("Start node not set")
        
        # Initialize execution
        current_node_id = self.start_node_id
        current_input = input_data
        max_steps = 100  # Prevent infinite loops
        step = 0
        
        # Execute until we reach the end node or max steps
        while current_node_id != self.end_node_id and step < max_steps:
            step += 1
            
            # Get current node
            current_node = self.nodes.get(current_node_id)
            if not current_node:
                raise ValueError(f"Node {current_node_id} not found in graph")
            
            # Update state
            self.state.set_current_node(current_node_id)
            
            # Execute node
            if current_node.handler:
                node_result = await current_node.handler(current_input, self.state)
            elif current_node.agent:
                # Build context for agent
                context = {
                    "graph_id": self.graph_id,
                    "node_id": current_node_id,
                    "step": step,
                    "state": self.state.to_dict()
                }
                
                # Process with agent
                agent_output = await current_node.agent.process(current_input, context)
                node_result = agent_output.to_dict()
            else:
                # Default passthrough
                node_result = current_input
            
            # Update node state
            node_state = self.state.get_node_state(current_node_id)
            if node_state:
                node_state.add_input(current_input)
                node_state.add_output(node_result)
            
            # Determine next node
            next_node_id = await self._get_next_node(current_node_id, node_result)
            
            if not next_node_id:
                # No valid next node, end execution
                break
            
            # Update for next iteration
            current_node_id = next_node_id
            current_input = node_result
        
        # Return final result
        return {
            "graph_id": self.graph_id,
            "steps": step,
            "output": current_input,
            "execution_path": self.state.execution_path,
            "success": current_node_id == self.end_node_id,
            "completed": step < max_steps
        }
    
    async def _get_next_node(self, current_node_id: str, result: Dict[str, Any]) -> Optional[str]:
        """
        Determine the next node to execute
        
        Args:
            current_node_id: ID of the current node
            result: Result of the current node execution
            
        Returns:
            ID of the next node, or None if no next node
        """
        # Find edges from current node
        outgoing_edges = [
            edge for edge in self.edges
            if edge.source_id == current_node_id
        ]
        
        if not outgoing_edges:
            return None
        
        # Check edge conditions
        valid_edges = []
        for edge in outgoing_edges:
            if not edge.condition or await edge.condition(result, self.state):
                valid_edges.append(edge)
        
        if not valid_edges:
            return None
        
        # Return first valid edge's target
        return valid_edges[0].target_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation"""
        return {
            "graph_id": self.graph_id,
            "nodes": {
                node_id: node.to_dict()
                for node_id, node in self.nodes.items()
            },
            "edges": [edge.to_dict() for edge in self.edges],
            "start_node_id": self.start_node_id,
            "end_node_id": self.end_node_id,
            "state": self.state.to_dict()
        }


class DynamicGraphBuilder:
    """Builder for dynamic execution graphs"""
    
    def __init__(self):
        """Initialize a dynamic graph builder"""
        pass
    
    def build_graph(
        self,
        agents: List[Agent],
        input_data: Dict[str, Any],
        tools: Optional[Dict[str, Any]] = None
    ) -> DynamicGraph:
        """
        Build a dynamic execution graph based on agents and input
        
        Args:
            agents: Available agents
            input_data: Input data for the graph
            tools: Available tools
            
        Returns:
            Built graph
        """
        # Create a new graph
        graph = DynamicGraph()
        
        # Analyze input to determine required capabilities
        required_capabilities = capability_registry.analyze_required_capabilities(input_data)
        
        # Create router node
        router_node = GraphNode(
            node_id="router",
            node_type="router",
            handler=self._create_router_handler()
        )
        graph.add_node(router_node)
        
        # Create end node
        end_node = GraphNode(
            node_id="end",
            node_type="end",
            handler=self._create_end_handler()
        )
        graph.add_node(end_node)
        
        # Determine initial agent based on required capabilities
        initial_agent = self._determine_initial_agent(agents, required_capabilities)
        
        if not initial_agent:
            raise ValueError("No suitable agent found for input")
        
        # Create initial agent node
        initial_node = GraphNode(
            node_id=f"agent_{initial_agent.agent_id}",
            node_type="agent",
            agent=initial_agent,
            metadata={
                "capabilities": list(capability_registry.get_agent_capabilities(initial_agent.agent_id))
            }
        )
        graph.add_node(initial_node)
        
        # Set start node to initial agent
        graph.set_start_node(initial_node.node_id)
        
        # Create agent nodes for all other agents
        agent_nodes = {}
        for agent in agents:
            if agent.agent_id == initial_agent.agent_id:
                agent_nodes[agent.agent_id] = initial_node
                continue
            
            node = GraphNode(
                node_id=f"agent_{agent.agent_id}",
                node_type="agent",
                agent=agent,
                metadata={
                    "capabilities": list(capability_registry.get_agent_capabilities(agent.agent_id))
                }
            )
            graph.add_node(node)
            agent_nodes[agent.agent_id] = node
        
        # Add edge from initial agent to router
        graph.add_edge(GraphEdge(
            source_id=initial_node.node_id,
            target_id=router_node.node_id
        ))
        
        # Add edges from router to agents
        for agent_id, node in agent_nodes.items():
            graph.add_edge(GraphEdge(
                source_id=router_node.node_id,
                target_id=node.node_id,
                condition=self._create_router_condition(agent_id)
            ))
        
        # Add edge from router to end
        graph.add_edge(GraphEdge(
            source_id=router_node.node_id,
            target_id=end_node.node_id,
            condition=self._create_end_condition()
        ))
        
        # Add edges from all agents to router
        for node in agent_nodes.values():
            graph.add_edge(GraphEdge(
                source_id=node.node_id,
                target_id=router_node.node_id
            ))
        
        # Set end node
        graph.set_end_node(end_node.node_id)
        
        return graph
    
    def _determine_initial_agent(self, agents: List[Agent], required_capabilities: List[str]) -> Optional[Agent]:
        """
        Determine the initial agent based on required capabilities
        
        Args:
            agents: Available agents
            required_capabilities: Required capabilities
            
        Returns:
            Initial agent
        """
        if not required_capabilities:
            # Default to the first agent
            return agents[0] if agents else None
        
        # Find the best agent for each capability
        for capability in required_capabilities:
            agent_scores = capability_registry.get_agents_with_capability(capability)
            for score in agent_scores:
                for agent in agents:
                    if agent.agent_id == score.agent_id:
                        return agent
        
        # If no agent found for capabilities, default to first agent
        return agents[0] if agents else None
    
    def _create_router_handler(self) -> Callable:
        """
        Create handler function for router node
        
        Returns:
            Router handler function
        """
        async def router_handler(input_data: Dict[str, Any], state: GraphState) -> Dict[str, Any]:
            # Router just passes through input
            return input_data
        
        return router_handler
    
    def _create_end_handler(self) -> Callable:
        """
        Create handler function for end node
        
        Returns:
            End handler function
        """
        async def end_handler(input_data: Dict[str, Any], state: GraphState) -> Dict[str, Any]:
            # End node just returns the final result
            return {
                "output": input_data,
                "message": "Execution completed successfully"
            }
        
        return end_handler
    
    def _create_router_condition(self, target_agent_id: str) -> Callable:
        """
        Create condition function for router edges
        
        Args:
            target_agent_id: ID of the target agent
            
        Returns:
            Condition function
        """
        async def condition(result: Dict[str, Any], state: GraphState) -> bool:
            # Check if there's a decision to route to this agent
            if "metadata" in result and "decision" in result["metadata"]:
                decision = result["metadata"]["decision"]
                if decision.get("action") == "delegate" and decision.get("target") == target_agent_id:
                    return True
            
            return False
        
        return condition
    
    def _create_end_condition(self) -> Callable:
        """
        Create condition function for end edge
        
        Returns:
            Condition function
        """
        async def condition(result: Dict[str, Any], state: GraphState) -> bool:
            # Check if there's a decision to end
            if "metadata" in result and "decision" in result["metadata"]:
                decision = result["metadata"]["decision"]
                if decision.get("action") == "final":
                    return True
            
            # Check if we've reached max steps
            if state.metadata.get("step_count", 0) >= 10:  # Arbitrary max steps
                return True
            
            return False
        
        return condition
