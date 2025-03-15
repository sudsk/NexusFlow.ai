"""
Core components for NexusFlow.ai

This package contains the core components of the NexusFlow system:
- Agent: Base class for all agents in the system
- Capability: Definition and registry for agent capabilities
- Flow: Orchestrator for agent workflows
- Node: Graph nodes for workflow representation
- State: State management for workflows
"""

from nexusflow.core.agent import Agent, AgentOutput, AgentDecision
from nexusflow.core.capability import (
    CapabilityType, 
    Capability, 
    CapabilityRegistry, 
    capability_registry
)
from nexusflow.core.flow import Flow
from nexusflow.core.node import Node, AgentNode, ToolNode, RouterNode
from nexusflow.core.state import FlowState, NodeState, GraphState

__all__ = [
    # Agent components
    'Agent',
    'AgentOutput',
    'AgentDecision',
    
    # Capability components
    'CapabilityType',
    'Capability',
    'CapabilityRegistry',
    'capability_registry',
    
    # Flow components
    'Flow',
    
    # Node components
    'Node',
    'AgentNode',
    'ToolNode',
    'RouterNode',
    
    # State components
    'FlowState',
    'NodeState',
    'GraphState',
]
