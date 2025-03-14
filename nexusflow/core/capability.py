"""
Capability System for NexusFlow.ai

This module defines the capability system that forms the foundation of NexusFlow's
dynamic agent architecture. Capabilities represent skills or abilities that agents
can possess, and they are used to dynamically route tasks and queries to the most
appropriate agents.
"""

from typing import Dict, List, Any, Optional, Set, Callable, Union
import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class CapabilityType(str, Enum):
    """Types of capabilities an agent can have"""
    REASONING = "reasoning"
    INFORMATION_RETRIEVAL = "information_retrieval"
    CODE_GENERATION = "code_generation"
    DATA_ANALYSIS = "data_analysis"
    SUMMARIZATION = "summarization"
    PLANNING = "planning"
    COORDINATION = "coordination"
    CRITIQUE = "critique"
    CREATIVE = "creative"
    DIALOGUE = "dialogue"
    
    @classmethod
    def all(cls) -> List[str]:
        """Return all capability types as strings"""
        return [c.value for c in cls]

@dataclass
class Capability:
    """Definition of an agent capability"""
    type: str
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    requires_tools: List[str] = field(default_factory=list)
    provides_output: List[str] = field(default_factory=list)
    requires_input: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert capability to dictionary"""
        return {
            "type": self.type,
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "requires_tools": self.requires_tools,
            "provides_output": self.provides_output,
            "requires_input": self.requires_input,
            "examples": self.examples
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Capability':
        """Create capability from dictionary"""
        return cls(
            type=data.get("type"),
            name=data.get("name"),
            description=data.get("description"),
            parameters=data.get("parameters", {}),
            requires_tools=data.get("requires_tools", []),
            provides_output=data.get("provides_output", []),
            requires_input=data.get("requires_input", []),
            examples=data.get("examples", [])
        )

@dataclass
class AgentCapabilityScore:
    """Score of an agent's capability"""
    agent_id: str
    capability_type: str
    score: float = 1.0  # Default score
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other):
        """Compare based on score for sorting"""
        if not isinstance(other, AgentCapabilityScore):
            return NotImplemented
        return self.score < other.score

class CapabilityRegistry:
    """Registry for agent capabilities"""
    
    def __init__(self):
        # Map of capability type to list of agent IDs with that capability
        self.capability_map: Dict[str, List[AgentCapabilityScore]] = {}
        
        # Map of agent ID to set of capability types
        self.agent_capabilities: Dict[str, Set[str]] = {}
        
        # Capability definitions
        self.capability_definitions: Dict[str, Capability] = {}
        
        # Register standard capabilities
        self._register_standard_capabilities()
    
    def _register_standard_capabilities(self):
        """Register standard capability definitions"""
        standard_capabilities = [
            Capability(
                type=CapabilityType.REASONING.value,
                name="General Reasoning",
                description="Ability to reason about general topics and answer questions",
                provides_output=["text"],
                requires_input=["query"]
            ),
            Capability(
                type=CapabilityType.INFORMATION_RETRIEVAL.value,
                name="Information Retrieval",
                description="Ability to retrieve relevant information from external sources",
                requires_tools=["search", "retrieve"],
                provides_output=["context", "sources"],
                requires_input=["query"]
            ),
            Capability(
                type=CapabilityType.CODE_GENERATION.value,
                name="Code Generation",
                description="Ability to generate code based on requirements",
                provides_output=["code", "explanation"],
                requires_input=["requirements"]
            ),
            Capability(
                type=CapabilityType.DATA_ANALYSIS.value,
                name="Data Analysis",
                description="Ability to analyze data and generate insights",
                requires_tools=["data_processing"],
                provides_output=["analysis", "visualization"],
                requires_input=["data"]
            ),
            Capability(
                type=CapabilityType.SUMMARIZATION.value,
                name="Summarization",
                description="Ability to summarize text content",
                provides_output=["summary"],
                requires_input=["content"]
            ),
            Capability(
                type=CapabilityType.PLANNING.value,
                name="Planning",
                description="Ability to create plans and break down tasks",
                provides_output=["plan", "steps"],
                requires_input=["goal"]
            ),
            Capability(
                type=CapabilityType.COORDINATION.value,
                name="Coordination",
                description="Ability to coordinate multiple agents and synthesize their outputs",
                provides_output=["coordination_result"],
                requires_input=["agent_outputs"]
            )
        ]
        
        for capability in standard_capabilities:
            self.register_capability_definition(capability)
    
    def register_capability_definition(self, capability: Capability):
        """Register a capability definition"""
        self.capability_definitions[capability.type] = capability
        logger.info(f"Registered capability definition: {capability.name}")
    
    def get_capability_definition(self, capability_type: str) -> Optional[Capability]:
        """Get a capability definition"""
        return self.capability_definitions.get(capability_type)
    
    def register_agent_capability(self, agent_id: str, capability_type: str, score: float = 1.0, metadata: Dict[str, Any] = None):
        """
        Register an agent's capability
        
        Args:
            agent_id: ID of the agent
            capability_type: Type of capability to register
            score: Score for this capability (0.0 to 1.0)
            metadata: Additional metadata about this capability
        """
        if capability_type not in self.capability_map:
            self.capability_map[capability_type] = []
        
        # Add to capability map
        capability_score = AgentCapabilityScore(
            agent_id=agent_id,
            capability_type=capability_type,
            score=score,
            metadata=metadata or {}
        )
        
        # Check if this agent already has this capability
        existing_scores = [cs for cs in self.capability_map[capability_type] if cs.agent_id == agent_id]
        if existing_scores:
            # Update existing score
            existing_idx = self.capability_map[capability_type].index(existing_scores[0])
            self.capability_map[capability_type][existing_idx] = capability_score
        else:
            # Add new score
            self.capability_map[capability_type].append(capability_score)
        
        # Sort by score (highest first)
        self.capability_map[capability_type].sort(key=lambda x: x.score, reverse=True)
        
        # Add to agent capabilities
        if agent_id not in self.agent_capabilities:
            self.agent_capabilities[agent_id] = set()
        self.agent_capabilities[agent_id].add(capability_type)
        
        logger.info(f"Registered agent {agent_id} with capability {capability_type} (score: {score})")
    
    def unregister_agent_capability(self, agent_id: str, capability_type: str):
        """Unregister an agent's capability"""
        if capability_type in self.capability_map:
            self.capability_map[capability_type] = [
                cs for cs in self.capability_map[capability_type] if cs.agent_id != agent_id
            ]
        
        if agent_id in self.agent_capabilities:
            self.agent_capabilities[agent_id].discard(capability_type)
        
        logger.info(f"Unregistered agent {agent_id} capability {capability_type}")
    
    def unregister_agent(self, agent_id: str):
        """Unregister all capabilities for an agent"""
        # Remove from all capability maps
        for capability_type in list(self.capability_map.keys()):
            self.capability_map[capability_type] = [
                cs for cs in self.capability_map[capability_type] if cs.agent_id != agent_id
            ]
        
        # Remove from agent capabilities
        if agent_id in self.agent_capabilities:
            del self.agent_capabilities[agent_id]
        
        logger.info(f"Unregistered all capabilities for agent {agent_id}")
    
    def get_agents_with_capability(self, capability_type: str) -> List[AgentCapabilityScore]:
        """
        Get all agents with a specific capability, sorted by score (highest first)
        
        Args:
            capability_type: Type of capability to search for
            
        Returns:
            List of agent capability scores, sorted by score
        """
        return self.capability_map.get(capability_type, [])
    
    def get_best_agent_for_capability(self, capability_type: str) -> Optional[str]:
        """
        Get the best agent for a specific capability based on score
        
        Args:
            capability_type: Type of capability to search for
            
        Returns:
            Agent ID of the best agent, or None if no agents have this capability
        """
        agents = self.get_agents_with_capability(capability_type)
        if not agents:
            return None
        return agents[0].agent_id
    
    def get_agent_capabilities(self, agent_id: str) -> Set[str]:
        """
        Get all capabilities for a specific agent
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Set of capability types
        """
        return self.agent_capabilities.get(agent_id, set())
    
    def agent_has_capability(self, agent_id: str, capability_type: str) -> bool:
        """
        Check if an agent has a specific capability
        
        Args:
            agent_id: ID of the agent
            capability_type: Type of capability to check
            
        Returns:
            True if the agent has the capability, False otherwise
        """
        return capability_type in self.get_agent_capabilities(agent_id)
    
    def analyze_required_capabilities(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Analyze input data to determine required capabilities
        
        This uses heuristics to determine what capabilities are needed to process the input.
        In a real implementation, this could use ML/NLP to better understand the requirements.
        
        Args:
            input_data: Input data to analyze
            
        Returns:
            List of required capability types
        """
        query = input_data.get("query", "").lower()
        required_capabilities = []
        
        # Check for information retrieval needs
        info_keywords = ["research", "find", "search", "information", "article", "news", "lookup"]
        if any(keyword in query for keyword in info_keywords):
            required_capabilities.append(CapabilityType.INFORMATION_RETRIEVAL.value)
        
        # Check for code generation needs
        code_keywords = ["code", "program", "function", "algorithm", "implement", "script"]
        if any(keyword in query for keyword in code_keywords):
            required_capabilities.append(CapabilityType.CODE_GENERATION.value)
        
        # Check for data analysis needs
        data_keywords = ["analyze", "analysis", "data", "statistics", "graph", "chart", "plot"]
        if any(keyword in query for keyword in data_keywords):
            required_capabilities.append(CapabilityType.DATA_ANALYSIS.value)
        
        # Check for summarization needs
        summary_keywords = ["summarize", "summary", "briefly", "shorten", "condense"]
        if any(keyword in query for keyword in summary_keywords):
            required_capabilities.append(CapabilityType.SUMMARIZATION.value)
        
        # Check for planning needs
        planning_keywords = ["plan", "steps", "how to", "process", "procedure"]
        if any(keyword in query for keyword in planning_keywords):
            required_capabilities.append(CapabilityType.PLANNING.value)
        
        # Always include reasoning as a fallback
        if not required_capabilities or CapabilityType.REASONING.value not in required_capabilities:
            required_capabilities.append(CapabilityType.REASONING.value)
        
        return required_capabilities

# Create global registry
capability_registry = CapabilityRegistry()
