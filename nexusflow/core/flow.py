"""
Flow orchestration system for NexusFlow.ai

This module defines the Flow class, which orchestrates the execution of agents
in a dynamic, capability-driven workflow.
"""

from typing import Dict, List, Any, Optional, Set, Union, Callable
import logging
import uuid
import asyncio
from datetime import datetime
import json

from .agent import Agent, AgentOutput, AgentDecision
from .capability import CapabilityType, capability_registry
from .state import FlowState

logger = logging.getLogger(__name__)

class Flow:
    """
    Flow orchestrator for dynamic agent workflows
    
    A Flow manages the execution of multiple agents, routing tasks based on
    agent capabilities and decisions. Flows are built dynamically based on
    the input and available agents.
    """
    
    def __init__(
        self,
        name: str,
        flow_id: Optional[str] = None,
        description: Optional[str] = None,
        agents: Optional[List[Agent]] = None,
        max_steps: int = 10,
        tools: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a flow
        
        Args:
            name: Human-readable name of the flow
            flow_id: Unique ID for the flow (generated if not provided)
            description: Description of the flow
            agents: List of agents in the flow
            max_steps: Maximum number of execution steps
            tools: Dictionary of available tools
        """
        self.name = name
        self.flow_id = flow_id or str(uuid.uuid4())
        self.description = description or f"Flow for {name}"
        self.agents = agents or []
        self.max_steps = max_steps
        self.tools = tools or {}
        
        # Create agent lookup maps
        self.agent_map = {agent.agent_id: agent for agent in self.agents}
        self.agent_name_map = {agent.name.lower(): agent for agent in self.agents}
        
        # Flow state
        self.state = FlowState()
        
        # Create execution trace for debugging and visualization
        self.execution_trace = []
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the flow with the given input
        
        Args:
            input_data: Input data for the flow
            
        Returns:
            Results of the flow execution
        """
        logger.info(f"Executing flow {self.name} ({self.flow_id})")
        
        # Initialize flow state
        self.state.initialize(input_data)
        
        # Save initial trace entry
        self._add_trace_entry("start", None, input_data, None)
        
        # Determine initial agent based on input capabilities
        current_agent = await self._determine_initial_agent(input_data)
        
        if not current_agent:
            raise ValueError("No suitable agent found for input")
        
        logger.info(f"Starting execution with agent {current_agent.name}")
        
        # Execute flow until max steps or termination
        step = 0
        final_output = None
        
        while step < self.max_steps:
            step += 1
            logger.info(f"Executing step {step} with agent {current_agent.name}")
            
            # Prepare context for agent
            context = self._build_agent_context(current_agent)
            
            # Process input with current agent
            agent_output = await current_agent.process(self.state.current_input, context)
            
            # Save output to state
            self.state.add_output(current_agent.agent_id, agent_output)
            
            # Get agent's decision
            decision = None
            if agent_output.metadata and "decision" in agent_output.metadata:
                decision = AgentDecision.from_dict(agent_output.metadata["decision"])
            
            # Save trace entry
            self._add_trace_entry("agent_execution", current_agent, self.state.current_input, agent_output, decision)
            
            # Process decision
            if not decision or decision.action == "final":
                logger.info(f"Agent {current_agent.name} provided final output")
                final_output = agent_output
                break
            
            elif decision.action == "delegate":
                # Find target agent
                target_agent = self._resolve_agent(decision.target)
                
                if not target_agent:
                    logger.warning(f"Target agent {decision.target} not found, using current agent")
                    final_output = agent_output
                    break
                
                logger.info(f"Delegating from {current_agent.name} to {target_agent.name}")
                
                # Update input for next agent
                self.state.current_input = {"query": decision.content}
                
                # Switch to target agent
                current_agent = target_agent
                
                # Save trace entry
                self._add_trace_entry("delegation", current_agent, self.state.current_input, None, decision)
            
            elif decision.action == "use_tool":
                tool_name = decision.tool_name
                tool_params = decision.tool_params
                
                if tool_name not in self.tools:
                    logger.warning(f"Tool {tool_name} not found")
                    # Continue with current agent, but send error
                    self.state.current_input = {
                        "query": f"Error: Tool {tool_name} not found. Please try again or provide a final answer."
                    }
                else:
                    logger.info(f"Using tool {tool_name}")
                    
                    # Execute tool
                    tool_result = await self._execute_tool(tool_name, tool_params)
                    
                    # Update input with tool result
                    self.state.current_input = {
                        "query": f"Tool {tool_name} result: {json.dumps(tool_result)}\n\nPlease continue processing."
                    }
                    
                    # Save trace entry
                    self._add_trace_entry("tool_execution", current_agent, tool_params, tool_result, decision)
            
            else:
                logger.warning(f"Unknown decision action: {decision.action}")
                final_output = agent_output
                break
        
        # If max steps reached without final output
        if not final_output:
            logger.warning(f"Max steps reached ({self.max_steps})")
            final_output = agent_output
        
        # Save final trace entry
        self._add_trace_entry("complete", current_agent, None, final_output)
        
        # Format final result
        result = {
            "flow_id": self.flow_id,
            "output": final_output.to_dict(),
            "steps": step,
            "execution_trace": self.execution_trace,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return result
    
    async def _determine_initial_agent(self, input_data: Dict[str, Any]) -> Optional[Agent]:
        """
        Determine the initial agent based on input capabilities
        
        Args:
            input_data: Input data to analyze
            
        Returns:
            Initial agent to use
        """
        # Analyze input to determine required capabilities
        required_capabilities = capability_registry.analyze_required_capabilities(input_data)
        
        if not required_capabilities:
            # Default to first agent with reasoning capability
            for agent in self.agents:
                if capability_registry.agent_has_capability(agent.agent_id, CapabilityType.REASONING.value):
                    return agent
            
            # If no agent has reasoning capability, use the first agent
            if self.agents:
                return self.agents[0]
            
            return None
        
        # Find best agent for the primary capability
        primary_capability = required_capabilities[0]
        agent_id = capability_registry.get_best_agent_for_capability(primary_capability)
        
        if agent_id and agent_id in self.agent_map:
            return self.agent_map[agent_id]
        
        # Try secondary capabilities
        for capability in required_capabilities[1:]:
            agent_id = capability_registry.get_best_agent_for_capability(capability)
            if agent_id and agent_id in self.agent_map:
                return self.agent_map[agent_id]
        
        # Default to first agent with reasoning capability
        for agent in self.agents:
            if capability_registry.agent_has_capability(agent.agent_id, CapabilityType.REASONING.value):
                return agent
        
        # If no agent has reasoning capability, use the first agent
        if self.agents:
            return self.agents[0]
        
        return None
    
    def _build_agent_context(self, agent: Agent) -> Dict[str, Any]:
        """
        Build context for an agent
        
        Args:
            agent: Agent to build context for
            
        Returns:
            Context dictionary
        """
        # Create basic context
        context = {
            "flow_id": self.flow_id,
            "flow_name": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "state": self.state.to_dict()
        }
        
        # Add information about available agents if the agent can delegate
        if agent.can_delegate:
            context["available_agents"] = [
                {
                    "name": a.name,
                    "agent_id": a.agent_id,
                    "description": a.description,
                    "capabilities": list(capability_registry.get_agent_capabilities(a.agent_id))
                }
                for a in self.agents if a.agent_id != agent.agent_id
            ]
        
        # Add information about available tools
        if agent.tool_names:
            context["tools"] = {
                tool_name: self.tools[tool_name]
                for tool_name in agent.tool_names
                if tool_name in self.tools
            }
        
        # Add previous messages
        context["messages"] = []
        for step in self.execution_trace:
            if step["type"] in ["agent_execution", "delegation"]:
                context["messages"].append({
                    "role": step.get("agent_name", "system"),
                    "content": step.get("output", {}).get("content", "") if "output" in step else step.get("input", {}).get("query", "")
                })
        
        return context
    
    def _resolve_agent(self, agent_identifier: str) -> Optional[Agent]:
        """
        Resolve an agent by ID or name
        
        Args:
            agent_identifier: Agent ID or name
            
        Returns:
            Resolved agent or None if not found
        """
        # Try direct lookup by ID
        if agent_identifier in self.agent_map:
            return self.agent_map[agent_identifier]
        
        # Try lookup by name (case-insensitive)
        agent_name_lower = agent_identifier.lower()
        if agent_name_lower in self.agent_name_map:
            return self.agent_name_map[agent_name_lower]
        
        # Try partial name match
        for name, agent in self.agent_name_map.items():
            if agent_name_lower in name or name in agent_name_lower:
                return agent
        
        return None
    
    async def _execute_tool(self, tool_name: str, tool_params: Dict[str, Any]) -> Any:
        """
        Execute a tool with the given parameters
        
        In a real implementation, this would call the actual tool.
        This is a placeholder that returns a mock result.
        
        Args:
            tool_name: Name of the tool to execute
            tool_params: Parameters for the tool
            
        Returns:
            Tool execution result
        """
        # Get tool definition
        tool = self.tools.get(tool_name)
        if not tool:
            return {"error": f"Tool {tool_name} not found"}
        
        # In a real implementation, this would validate parameters and execute the tool
        # For now, we'll return a mock result
        
        # Simulate async tool execution
        await asyncio.sleep(0.1)
        
        if tool_name == "web_search":
            query = tool_params.get("query", "")
            return {
                "results": [
                    {"title": f"Result 1 for {query}", "snippet": "This is the first result snippet"},
                    {"title": f"Result 2 for {query}", "snippet": "This is the second result snippet"},
                ],
                "query": query
            }
        
        elif tool_name == "code_execution":
            code = tool_params.get("code", "")
            return {
                "result": f"Executed code: {code[:50]}...",
                "output": "Code execution output would be here"
            }
        
        elif tool_name == "data_analysis":
            data = tool_params.get("data", "")
            analysis_type = tool_params.get("analysis_type", "")
            return {
                "analysis": f"Analysis of type {analysis_type} on data {data[:50]}...",
                "charts": ["chart1", "chart2"]
            }
        
        return {"result": f"Executed tool {tool_name} with params {json.dumps(tool_params)}"}
    
    def _add_trace_entry(
        self,
        entry_type: str,
        agent: Optional[Agent],
        input_data: Optional[Dict[str, Any]],
        output: Optional[AgentOutput],
        decision: Optional[AgentDecision] = None
    ):
        """
        Add an entry to the execution trace
        
        Args:
            entry_type: Type of trace entry
            agent: Agent involved (if any)
            input_data: Input data (if any)
            output: Output data (if any)
            decision: Agent decision (if any)
        """
        entry = {
            "type": entry_type,
            "timestamp": datetime.utcnow().isoformat(),
            "step": len(self.execution_trace) + 1
        }
        
        if agent:
            entry["agent_id"] = agent.agent_id
            entry["agent_name"] = agent.name
        
        if input_data:
            entry["input"] = input_data
        
        if output:
            entry["output"] = output.to_dict()
        
        if decision:
            entry["decision"] = decision.to_dict()
        
        self.execution_trace.append(entry)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert flow to dictionary representation"""
        return {
            "flow_id": self.flow_id,
            "name": self.name,
            "description": self.description,
            "agents": [agent.to_dict() for agent in self.agents],
            "max_steps": self.max_steps,
            "tools": {name: {k: v for k, v in tool.items() if k != "handler"} for name, tool in self.tools.items()},
            "execution_trace": self.execution_trace
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], agents: Optional[List[Agent]] = None) -> 'Flow':
        """Create flow from dictionary"""
        # If agents not provided, create them from the data
        if not agents and "agents" in data:
            agents = [Agent.from_dict(agent_data) for agent_data in data.get("agents", [])]
        
        return cls(
            name=data.get("name", "Unnamed Flow"),
            flow_id=data.get("flow_id"),
            description=data.get("description"),
            agents=agents,
            max_steps=data.get("max_steps", 10),
            tools=data.get("tools", {})
        )
        
    @classmethod
    def from_database(cls, flow_record, session):
        """Create a flow from a database record"""
        config = flow_record.config
        # Create agents based on config...
        agents = []
        
        return cls(
            name=flow_record.name,
            flow_id=flow_record.id,
            description=flow_record.description,
            agents=agents,
            max_steps=config.get("max_steps", 10),
            tools=config.get("tools", {})
        )
