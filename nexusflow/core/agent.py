"""
Agent system for NexusFlow.ai

This module defines the base Agent class that forms the foundation of all agents
in the NexusFlow system. Agents have capabilities, can process input, and
can produce output to be used by other agents.
"""

from typing import Dict, List, Any, Optional, Set, Union, Callable
import logging
import uuid
import json
import asyncio
from datetime import datetime

from .capability import CapabilityType, capability_registry

logger = logging.getLogger(__name__)

class AgentOutput:
    """Container for agent output"""
    
    def __init__(
        self,
        content: Any,
        output_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.output_type = output_type
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert output to dictionary"""
        return {
            "content": self.content,
            "output_type": self.output_type,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentOutput':
        """Create output from dictionary"""
        return cls(
            content=data.get("content"),
            output_type=data.get("output_type", "text"),
            metadata=data.get("metadata", {})
        )

class AgentDecision:
    """Represents a routing decision made by an agent"""
    
    def __init__(
        self,
        action: str,  # "delegate", "respond", "use_tool", "final"
        target: Optional[str] = None,  # Agent ID for delegation
        content: Optional[Any] = None,
        reasoning: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_params: Optional[Dict[str, Any]] = None
    ):
        self.action = action
        self.target = target
        self.content = content
        self.reasoning = reasoning
        self.tool_name = tool_name
        self.tool_params = tool_params or {}
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert decision to dictionary"""
        return {
            "action": self.action,
            "target": self.target,
            "content": self.content,
            "reasoning": self.reasoning,
            "tool_name": self.tool_name,
            "tool_params": self.tool_params,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentDecision':
        """Create decision from dictionary"""
        return cls(
            action=data.get("action", "respond"),
            target=data.get("target"),
            content=data.get("content"),
            reasoning=data.get("reasoning"),
            tool_name=data.get("tool_name"),
            tool_params=data.get("tool_params", {})
        )

class Agent:
    """Base agent class"""
    
    def __init__(
        self,
        name: str,
        agent_id: Optional[str] = None,
        description: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        model_provider: str = "openai",
        model_name: str = "gpt-4",
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tool_names: Optional[List[str]] = None,
        can_delegate: bool = True
    ):
        """
        Initialize an agent
        
        Args:
            name: Human-readable name of the agent
            agent_id: Unique ID for the agent (generated if not provided)
            description: Description of the agent
            capabilities: List of capability types
            model_provider: Provider for the language model
            model_name: Name of the language model
            system_message: System message for the language model
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            tool_names: List of tool names the agent can use
            can_delegate: Whether the agent can delegate to other agents
        """
        self.name = name
        self.agent_id = agent_id or str(uuid.uuid4())
        self.description = description or f"Agent for {name}"
        self.model_provider = model_provider
        self.model_name = model_name
        self.system_message = system_message or self._get_default_system_message()
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tool_names = tool_names or []
        self.can_delegate = can_delegate
        
        # Register capabilities
        self._register_capabilities(capabilities or [])
        
        # Agent state
        self.state = {}
        self.memory = []
        self.decisions = []
    
    def _register_capabilities(self, capabilities: List[str]):
        """Register agent capabilities with the registry"""
        for capability in capabilities:
            # Default to 1.0 score for now; in the future, we might have more sophisticated scoring
            capability_registry.register_agent_capability(
                agent_id=self.agent_id,
                capability_type=capability,
                score=1.0,
                metadata={
                    "model": f"{self.model_provider}/{self.model_name}",
                    "temperature": self.temperature
                }
            )
    
    def _get_default_system_message(self) -> str:
        """Get default system message based on agent configuration"""
        return f"""You are {self.name}, an AI assistant with the following capabilities:
- Analyze and understand user queries
- Provide helpful, accurate responses
- Be concise and clear in your answers
"""
    
    async def process(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> AgentOutput:
        """
        Process input data and generate output
        
        Args:
            input_data: Input data to process
            context: Additional context for processing
            
        Returns:
            Agent output
        """
        context = context or {}
        
        # Log processing start
        logger.info(f"Agent {self.name} ({self.agent_id}) processing input")
        
        # Build the prompt
        prompt = self._build_prompt(input_data, context)
        
        # Generate response using the LLM
        response = await self._generate_response(prompt)
        
        # Parse the response to get output and decisions
        output, decision = self._parse_response(response, input_data, context)
        
        # Save decision
        if decision:
            self.decisions.append(decision)
        
        # Update agent memory
        self._update_memory(input_data, output, context)
        
        return output
    
    def _build_prompt(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Build prompt for the language model
        
        Args:
            input_data: Input data to process
            context: Additional context
            
        Returns:
            Prompt string
        """
        # Start with basic query
        query = input_data.get("query", "")
        
        # Add context about available agents if this agent can delegate
        available_agents = ""
        if self.can_delegate and "available_agents" in context:
            available_agents = "\n\nAvailable agents:\n"
            for agent_info in context["available_agents"]:
                capabilities = ", ".join(agent_info.get("capabilities", []))
                available_agents += f"- {agent_info['name']}: {capabilities}\n"
        
        # Add context about available tools
        available_tools = ""
        if self.tool_names and "tools" in context:
            available_tools = "\n\nAvailable tools:\n"
            for tool_name in self.tool_names:
                if tool_name in context["tools"]:
                    tool_info = context["tools"][tool_name]
                    available_tools += f"- {tool_name}: {tool_info['description']}\n"
        
        # Add previous messages if available
        conversation_history = ""
        if "messages" in context:
            conversation_history = "\n\nPrevious messages:\n"
            for msg in context["messages"]:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                conversation_history += f"{role}: {content}\n"
        
        # Combine all parts
        prompt = f"{query}{available_agents}{available_tools}{conversation_history}"
        
        # Add decision instructions
        prompt += self._get_decision_instructions()
        
        return prompt
    
    def _get_decision_instructions(self) -> str:
        """Get instructions for making decisions"""
        instructions = "\n\nBased on the above, choose one of the following actions:\n"
        
        if self.can_delegate:
            instructions += "- Delegate to another agent by writing [ACTION: delegate to agent_name]\n"
        
        if self.tool_names:
            instructions += "- Use a tool by writing [TOOL: tool_name] followed by parameters in JSON\n"
            
        instructions += "- Provide a final answer by writing [ACTION: final]\n"
        
        return instructions
    
    async def _generate_response(self, prompt: str) -> str:
        """
        Generate response using the language model
        
        In a real implementation, this would call an actual LLM API.
        This is a placeholder that returns a mock response.
        
        Args:
            prompt: Prompt for the language model
            
        Returns:
            Generated response
        """
        # This is where you'd call your LLM provider
        # For now, we'll return a mock response
        
        # Simulate async call to LLM
        await asyncio.sleep(0.1)
        
        # Mock response based on prompt
        if "code" in prompt.lower() or "programming" in prompt.lower():
            return """I'll help with this coding task.

[ACTION: delegate to coding_agent]
"""
        elif "research" in prompt.lower() or "information" in prompt.lower():
            return """Let me search for some information.

[TOOL: web_search]
{
    "query": "latest information on this topic"
}
"""
        else:
            return """Here's my final answer based on my analysis.

This is a detailed response to the query that provides helpful information.

[ACTION: final]
"""
    
    def _parse_response(self, response: str, input_data: Dict[str, Any], context: Dict[str, Any]) -> tuple[AgentOutput, Optional[AgentDecision]]:
        """
        Parse the LLM response to extract output and decisions
        
        Args:
            response: LLM response
            input_data: Original input data
            context: Processing context
            
        Returns:
            Tuple of (output, decision)
        """
        # Default output is the full response
        output_content = response
        
        # Check for decision markers
        decision = None
        
        # Check for delegation
        delegate_match = None
        if self.can_delegate:
            import re
            delegate_match = re.search(r'\[ACTION:\s*delegate\s+to\s+(\w+)\]', response)
            
        if delegate_match:
            target_agent = delegate_match.group(1)
            decision = AgentDecision(
                action="delegate",
                target=target_agent,
                content=response,
                reasoning=f"Delegating to {target_agent} based on their capabilities"
            )
        
        # Check for tool usage
        tool_match = None
        if self.tool_names:
            import re
            tool_match = re.search(r'\[TOOL:\s*(\w+)\](.*?)(\[\/?TOOL\]|\Z)', response, re.DOTALL)
            
        if tool_match:
            tool_name = tool_match.group(1)
            tool_params_str = tool_match.group(2).strip()
            
            # Parse tool parameters
            tool_params = {}
            try:
                import json
                tool_params = json.loads(tool_params_str)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract parameters heuristically
                param_matches = re.findall(r'(\w+)\s*:\s*([^,\n]+)', tool_params_str)
                for key, value in param_matches:
                    tool_params[key.strip()] = value.strip()
            
            decision = AgentDecision(
                action="use_tool",
                tool_name=tool_name,
                tool_params=tool_params,
                content=response,
                reasoning=f"Using tool {tool_name} to get additional information"
            )
        
        # Check for final action
        final_match = re.search(r'\[ACTION:\s*final\]', response)
        if final_match:
            decision = AgentDecision(
                action="final",
                content=response,
                reasoning="Providing final response"
            )
        
        # If no decision was identified, default to final
        if not decision:
            decision = AgentDecision(
                action="final",
                content=response,
                reasoning="Default final response"
            )
        
        # Create the output object
        output = AgentOutput(
            content=output_content,
            output_type="text",
            metadata={
                "agent_id": self.agent_id,
                "agent_name": self.name,
                "model": f"{self.model_provider}/{self.model_name}",
                "decision": decision.to_dict() if decision else None
            }
        )
        
        return output, decision
