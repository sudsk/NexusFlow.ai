"""
Reasoning Agent for NexusFlow.ai

This module defines the ReasoningAgent class, which specializes in general reasoning
and problem solving tasks.
"""

from typing import Dict, List, Any, Optional
import logging

from nexusflow.core.agent import Agent, AgentOutput
from nexusflow.core.capability import CapabilityType

logger = logging.getLogger(__name__)

class ReasoningAgent(Agent):
    """
    Agent specialized in general reasoning and problem solving
    
    The ReasoningAgent is a versatile agent that can handle a wide range of
    reasoning tasks, including:
    - Answering questions based on provided context
    - Breaking down complex problems into steps
    - Explaining concepts clearly and accurately
    - Making logical inferences and deductions
    """
    
    def __init__(
        self,
        name: str = "Reasoning Agent",
        agent_id: Optional[str] = None,
        model_provider: str = "openai",
        model_name: str = "gpt-4",
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize a reasoning agent
        
        Args:
            name: Human-readable name of the agent
            agent_id: Unique ID for the agent (generated if not provided)
            model_provider: Provider for the language model
            model_name: Name of the language model
            temperature: Temperature for generation (lower for more deterministic output)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters to pass to Agent constructor
        """
        # Set default system message if not provided
        system_message = kwargs.pop('system_message', None) or self._get_default_system_message()
        
        # Initialize base agent
        super().__init__(
            name=name,
            agent_id=agent_id,
            description="An agent specialized in reasoning and problem solving",
            capabilities=[CapabilityType.REASONING.value],
            model_provider=model_provider,
            model_name=model_name,
            system_message=system_message,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def _get_default_system_message(self) -> str:
        """Get default system message for reasoning agent"""
        return """You are a reasoning agent specialized in problem solving and logical analysis.

Your strengths:
- Breaking down complex problems into manageable parts
- Providing clear, step-by-step reasoning
- Maintaining objectivity and avoiding bias
- Drawing logical conclusions from available information
- Explaining your thought process in a transparent way

When responding:
1. Take time to understand the problem thoroughly
2. Identify key variables and constraints
3. Structure your reasoning in clear, logical steps
4. Consider alternative perspectives and approaches
5. Provide a conclusion that follows from your reasoning

Remember that the quality of your reasoning is more important than the speed of your response. It's better to be thorough and correct than quick but incomplete."""
    
    async def _build_specialized_prompt(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Build a specialized prompt for reasoning tasks
        
        Args:
            input_data: Input data to process
            context: Additional context for processing
            
        Returns:
            Specialized prompt string
        """
        # Start with basic query
        query = input_data.get("query", "")
        
        # Add reasoning-specific instructions
        reasoning_instructions = """
Please approach this problem systematically:

1. Understand the question/problem
2. Identify key information and constraints
3. Apply relevant reasoning methods
4. Develop your answer step-by-step
5. Check your logic for inconsistencies
6. Provide a clear conclusion
"""
        
        # Combine with any additional context provided
        additional_context = ""
        if "context" in input_data:
            additional_context = f"\n\nAdditional context:\n{input_data['context']}"
        
        # Combine all parts
        full_prompt = f"{query}{additional_context}\n{reasoning_instructions}"
        
        return full_prompt
    
    async def process(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> AgentOutput:
        """
        Process input data with specialized reasoning capabilities
        
        Args:
            input_data: Input data to process
            context: Additional context for processing
            
        Returns:
            Agent output
        """
        context = context or {}
        
        # Use specialized prompt building if this is a direct query
        if not context.get("is_delegation", False):
            # Check if input is suitable for reasoning
            if self._is_reasoning_task(input_data):
                # Build specialized prompt
                specialized_prompt = await self._build_specialized_prompt(input_data, context)
                
                # Update input data with specialized prompt
                input_data = {**input_data, "query": specialized_prompt}
        
        # Call the base agent's process method
        return await super().process(input_data, context)
    
    def _is_reasoning_task(self, input_data: Dict[str, Any]) -> bool:
        """
        Determine if the input is suitable for reasoning
        
        Args:
            input_data: Input data to check
            
        Returns:
            True if the input is a reasoning task
        """
        # Extract query
        query = input_data.get("query", "").lower()
        
        # Check for reasoning indicators
        reasoning_indicators = [
            "why", "how", "explain", "analyze", "reason", "think through",
            "steps", "logic", "argument", "evidence", "conclusion",
            "consider", "evaluate", "assess", "solve", "problem"
        ]
        
        # Check if any indicators are present
        for indicator in reasoning_indicators:
            if indicator in query:
                return True
        
        # Default to True for this specialized agent
        return True
