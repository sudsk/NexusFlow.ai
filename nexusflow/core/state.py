"""
State management for NexusFlow.ai

This module defines state management classes that track the execution state
of agents and flows in the NexusFlow system.
"""

from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import copy
import json

from .agent import AgentOutput

class FlowState:
    """State of a flow execution"""
    
    def __init__(self):
        """Initialize flow state"""
        # Initial input data
        self.initial_input: Dict[str, Any] = {}
        
        # Current input being processed
        self.current_input: Dict[str, Any] = {}
        
        # Outputs from each agent, keyed by agent ID
        self.outputs: Dict[str, List[AgentOutput]] = {}
        
        # Execution metadata
        self.metadata: Dict[str, Any] = {
            "start_time": None,
            "last_update_time": None,
            "steps": 0
        }
        
        # Flow-wide scratchpad for agent communication
        self.scratchpad: Dict[str, Any] = {}
    
    def initialize(self, input_data: Dict[str, Any]) -> None:
        """
        Initialize state with input data
        
        Args:
            input_data: Initial input data
        """
        self.initial_input = copy.deepcopy(input_data)
        self.current_input = copy.deepcopy(input_data)
        self.metadata["start_time"] = datetime.utcnow().isoformat()
        self.metadata["last_update_time"] = self.metadata["start_time"]
        self.metadata["steps"] = 0
    
    def add_output(self, agent_id: str, output: AgentOutput) -> None:
        """
        Add agent output to state
        
        Args:
            agent_id: ID of the agent
            output: Output from the agent
        """
        if agent_id not in self.outputs:
            self.outputs[agent_id] = []
        
        self.outputs[agent_id].append(output)
        self.metadata["last_update_time"] = datetime.utcnow().isoformat()
        self.metadata["steps"] += 1
    
    def get_agent_outputs(self, agent_id: str) -> List[AgentOutput]:
        """
        Get outputs from a specific agent
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            List of outputs from the agent
        """
        return self.outputs.get(agent_id, [])
    
    def get_last_output(self, agent_id: str) -> Optional[AgentOutput]:
        """
        Get the last output from a specific agent
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Last output from the agent, or None if no outputs
        """
        outputs = self.get_agent_outputs(agent_id)
        if not outputs:
            return None
        return outputs[-1]
    
    def get_all_outputs(self) -> List[AgentOutput]:
        """
        Get all outputs from all agents
        
        Returns:
            List of all outputs
        """
        all_outputs = []
        for agent_outputs in self.outputs.values():
            all_outputs.extend(agent_outputs)
        return all_outputs
    
    def set_scratchpad_value(self, key: str, value: Any) -> None:
        """
        Set a value in the scratchpad
        
        Args:
            key: Key to set
            value: Value to set
        """
        self.scratchpad[key] = value
    
    def get_scratchpad_value(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the scratchpad
        
        Args:
            key: Key to get
            default: Default value if key not found
            
        Returns:
            Value from scratchpad
        """
        return self.scratchpad.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary representation"""
        return {
            "initial_input": self.initial_input,
            "current_input": self.current_input,
            "outputs": {
                agent_id: [output.to_dict() for output in outputs]
                for agent_id, outputs in self.outputs.items()
            },
            "metadata": self.metadata,
            "scratchpad": self.scratchpad
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlowState':
        """Create state from dictionary"""
        state = cls()
        
        state.initial_input = data.get("initial_input", {})
        state.current_input = data.get("current_input", {})
        state.metadata = data.get("metadata", {
            "start_time": datetime.utcnow().isoformat(),
            "last_update_time": datetime.utcnow().isoformat(),
            "steps": 0
        })
        state.scratchpad = data.get("scratchpad", {})
        
        # Convert output dictionaries back to AgentOutput objects
        outputs_dict = data.get("outputs", {})
        for agent_id, outputs in outputs_dict.items():
            state.outputs[agent_id] = [
                AgentOutput.from_dict(output_dict)
                for output_dict in outputs
            ]
        
        return state


class NodeState:
    """State of a graph node in a flow"""
    
    def __init__(self, node_id: str, node_type: str):
        """
        Initialize node state
        
        Args:
            node_id: ID of the node
            node_type: Type of the node
        """
        self.node_id = node_id
        self.node_type = node_type
        self.inputs = []
        self.outputs = []
        self.metadata = {
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "execution_count": 0
        }
    
    def add_input(self, input_data: Any) -> None:
        """
        Add input to the node
        
        Args:
            input_data: Input data
        """
        self.inputs.append({
            "data": input_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.metadata["last_updated"] = datetime.utcnow().isoformat()
    
    def add_output(self, output_data: Any) -> None:
        """
        Add output from the node
        
        Args:
            output_data: Output data
        """
        self.outputs.append({
            "data": output_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.metadata["last_updated"] = datetime.utcnow().isoformat()
        self.metadata["execution_count"] += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node state to dictionary representation"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NodeState':
        """Create node state from dictionary"""
        state = cls(
            node_id=data.get("node_id", "unknown"),
            node_type=data.get("node_type", "unknown")
        )
        
        state.inputs = data.get("inputs", [])
        state.outputs = data.get("outputs", [])
        state.metadata = data.get("metadata", {
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "execution_count": 0
        })
        
        return state


class GraphState:
    """State of a graph in a flow"""
    
    def __init__(self):
        """Initialize graph state"""
        self.nodes: Dict[str, NodeState] = {}
        self.edges: List[Dict[str, str]] = []
        self.current_node_id: Optional[str] = None
        self.execution_path: List[str] = []
        self.metadata: Dict[str, Any] = {
            "start_time": datetime.utcnow().isoformat(),
            "last_update_time": datetime.utcnow().isoformat(),
            "step_count": 0
        }
    
    def add_node(self, node_id: str, node_type: str) -> NodeState:
        """
        Add a node to the graph
        
        Args:
            node_id: ID of the node
            node_type: Type of the node
            
        Returns:
            State of the new node
        """
        node_state = NodeState(node_id, node_type)
        self.nodes[node_id] = node_state
        return node_state
    
    def add_edge(self, source_id: str, target_id: str, edge_type: str = "default") -> None:
        """
        Add an edge to the graph
        
        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            edge_type: Type of the edge
        """
        self.edges.append({
            "source": source_id,
            "target": target_id,
            "type": edge_type,
            "created_at": datetime.utcnow().isoformat()
        })
    
    def set_current_node(self, node_id: str) -> None:
        """
        Set the current node
        
        Args:
            node_id: ID of the node
        """
        self.current_node_id = node_id
        self.execution_path.append(node_id)
        self.metadata["last_update_time"] = datetime.utcnow().isoformat()
        self.metadata["step_count"] += 1
    
    def get_node_state(self, node_id: str) -> Optional[NodeState]:
        """
        Get the state of a node
        
        Args:
            node_id: ID of the node
            
        Returns:
            State of the node, or None if not found
        """
        return self.nodes.get(node_id)
    
    def get_current_node_state(self) -> Optional[NodeState]:
        """
        Get the state of the current node
        
        Returns:
            State of the current node, or None if no current node
        """
        if not self.current_node_id:
            return None
        return self.get_node_state(self.current_node_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph state to dictionary representation"""
        return {
            "nodes": {
                node_id: node_state.to_dict()
                for node_id, node_state in self.nodes.items()
            },
            "edges": self.edges,
            "current_node_id": self.current_node_id,
            "execution_path": self.execution_path,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GraphState':
        """Create graph state from dictionary"""
        state = cls()
        
        # Create nodes
        nodes_dict = data.get("nodes", {})
        for node_id, node_data in nodes_dict.items():
            state.nodes[node_id] = NodeState.from_dict(node_data)
        
        state.edges = data.get("edges", [])
        state.current_node_id = data.get("current_node_id")
        state.execution_path = data.get("execution_path", [])
        state.metadata = data.get("metadata", {
            "start_time": datetime.utcnow().isoformat(),
            "last_update_time": datetime.utcnow().isoformat(),
            "step_count": 0
        })
        
        return state
