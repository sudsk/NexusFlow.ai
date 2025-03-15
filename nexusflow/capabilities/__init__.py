"""
Capability implementations for NexusFlow.ai

This package contains implementations of specific capabilities:
- Reasoning: General reasoning capability
- Retrieval: Information retrieval capability
- Coding: Code generation capability
- Analysis: Data analysis capability
"""

from nexusflow.capabilities.reasoning import ReasoningCapability
from nexusflow.capabilities.retrieval import RetrievalCapability
from nexusflow.capabilities.coding import CodingCapability
from nexusflow.capabilities.analysis import AnalysisCapability

# Create instances of capabilities
reasoning_capability = ReasoningCapability()
retrieval_capability = RetrievalCapability()
coding_capability = CodingCapability()
analysis_capability = AnalysisCapability()

# List of all capabilities
all_capabilities = [
    reasoning_capability,
    retrieval_capability,
    coding_capability,
    analysis_capability
]

__all__ = [
    'ReasoningCapability',
    'RetrievalCapability',
    'CodingCapability',
    'AnalysisCapability',
    'reasoning_capability',
    'retrieval_capability',
    'coding_capability',
    'analysis_capability',
    'all_capabilities'
]
