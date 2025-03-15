"""
NexusFlow.ai - Dynamic Agent Orchestration

NexusFlow is a framework for building AI agent systems with dynamic, capability-driven
orchestration. Unlike traditional workflow systems that rely on predefined structures,
NexusFlow enables fluid intelligence networks where the execution path emerges naturally
from agent capabilities and relationships.
"""

__version__ = "0.1.0"

from nexusflow.core import (
    Agent, 
    AgentOutput, 
    AgentDecision,
    CapabilityType, 
    Capability, 
    CapabilityRegistry,
    capability_registry,
    Flow,
    Node,
    AgentNode,
    ToolNode,
    RouterNode,
    FlowState,
    NodeState,
    GraphState
)

__all__ = [
    # Core components
    'Agent',
    'AgentOutput',
    'AgentDecision',
    'CapabilityType',
    'Capability',
    'CapabilityRegistry',
    'capability_registry',
    'Flow',
    'Node',
    'AgentNode',
    'ToolNode',
    'RouterNode',
    'FlowState',
    'NodeState',
    'GraphState',
    
    # Version
    '__version__',
]
