"""
Analysis Agent for NexusFlow.ai

This module defines the AnalysisAgent class, which specializes in data analysis
and insight generation tasks.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import logging
import json
import re

from nexusflow.core.agent import Agent, AgentOutput
from nexusflow.core.capability import CapabilityType

logger = logging.getLogger(__name__)

class AnalysisAgent(Agent):
    """
    Agent specialized in data analysis
    
    The AnalysisAgent focuses on analyzing data and generating insights, including:
    - Performing statistical analysis
    - Identifying patterns and trends
    - Creating data visualizations
    - Interpreting results
    - Making recommendations based on data
    """
    
    def __init__(
        self,
        name: str = "Analysis Agent",
        agent_id: Optional[str] = None,
        model_provider: str = "openai",
        model_name: str = "gpt-4",
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        analysis_tools: List[str] = None,
        **kwargs
    ):
        """
        Initialize an analysis agent
        
        Args:
            name: Human-readable name of the agent
            agent_id: Unique ID for the agent (generated if not provided)
            model_provider: Provider for the language model
            model_name: Name of the language model
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            analysis_tools: List of analysis tool names to use
            **kwargs: Additional parameters to pass to Agent constructor
        """
        # Set default system message if not provided
        system_message = kwargs.pop('system_message', None) or self._get_default_system_message()
        
        # Set default analysis tools if not provided
        if analysis_tools is None:
            analysis_tools = ["data_analysis", "code_execution"]
        
        # Set default tool names based on analysis tools
        tool_names = kwargs.pop('tool_names', None) or analysis_tools
        
        # Initialize base agent
        super().__init__(
            name=name,
            agent_id=agent_id,
            description="An agent specialized in data analysis and insight generation",
            capabilities=[CapabilityType.DATA_ANALYSIS.value, CapabilityType.REASONING.value],
            model_provider=model_provider,
            model_name=model_name,
            system_message=system_message,
            temperature=temperature,
            max_tokens=max_tokens,
            tool_names=tool_names,
            **kwargs
        )
        
        # Store analysis-specific properties
        self.analysis_tools = analysis_tools
        self.analysis_history = []
        self.supported_analysis_types = [
            "descriptive", "exploratory", "statistical", "predictive", 
            "causal", "prescriptive", "clustering", "classification",
            "correlation", "regression", "time_series", "anomaly_detection"
        ]
    
    def _get_default_system_message(self) -> str:
        """Get default system message for analysis agent"""
        return """You are an analysis agent specialized in analyzing data and generating insights.

Your strengths:
- Performing statistical analysis on datasets
- Identifying patterns, trends, and outliers
- Visualizing data effectively
- Drawing meaningful insights from complex information
- Making data-driven recommendations
- Explaining analytical findings clearly

When analyzing data:
1. Understand the analytical question thoroughly
2. Examine the data structure and quality
3. Choose appropriate analytical methods
4. Execute the analysis rigorously
5. Interpret results carefully, considering limitations
6. Communicate findings clearly with visualizations when helpful

Remember to leverage analysis tools when needed rather than relying solely on your internal reasoning."""
