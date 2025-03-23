# backend/adapters/langgraph/langgraph_adapter.py
from typing import Dict, List, Any, Optional, Callable, Awaitable, Union
import asyncio
import logging
import json
import importlib
import inspect
from datetime import datetime

from ...adapters.interfaces.base_adapter import FrameworkAdapter

logger = logging.getLogger(__name__)

class LangGraphAdapter(FrameworkAdapter):
    """Adapter for LangGraph framework"""

    def __init__(self):
        # Check if langgraph is installed
        try:
            self.langgraph_available = True
            import langchain
            self.langchain_version = langchain.__version__
            
            # Import LangGraph modules conditionally
            try:
                import langgraph
                from langgraph.graph import StateGraph
                self.StateGraph = StateGraph
                self.langgraph_version = langgraph.__version__
                
                # Check if we have LangChain components
                try:
                    from langchain_experimental import pydantic_v1
                    from langchain.agents import AgentExecutor
                    from langchain.tools import tool
                    self.AgentExecutor = AgentExecutor
                    self.tool_decorator = tool
                    self.has_full_imports = True
                except ImportError as e:
                    logger.warning(f"LangChain agent components not available: {str(e)}")
                    self.has_full_imports = False
                    
            except ImportError as e:
                logger.warning(f"LangGraph components not available: {str(e)}")
                self.langgraph_available = False
                self.has_full_imports = False
                    
        except ImportError:
            self.langgraph_available = False
            logger.warning("LangChain not installed - some functionality may be limited")
            self.has_full_imports = False

    def get_framework_name(self) -> str:
        return "langgraph"
    
    def convert_flow(self, flow_config: Dict[str, Any]) -> Any:
        """Convert NexusFlow configuration to LangGraph format"""
        # Extract components from flow config
        agents = flow_config.get("agents", [])
        tools = flow_config.get("tools", {})
        max_steps = flow_config.get("max_steps", 10)
        
        # Create a proper LangGraph configuration
        # For MVP, we'll use a simplified representation that can be executed
        langgraph_config = {
            "type": "langgraph_flow",
            "nodes": [],
            "edges": [],
            "agents": [],
            "tools": {},
            "entry_point": None,
            "max_iterations": max_steps,
            "original_config": flow_config
        }
        
        # Process agents
        for i, agent in enumerate(agents):
            agent_id = agent.get("agent_id", f"agent-{i}")
            agent_config = {
                "id": agent_id,
                "name": agent.get("name", f"Agent {i+1}"),
                "model_provider": agent.get("model_provider", "openai"),
                "model_name": agent.get("model_name", "gpt-4"),
                "temperature": agent.get("temperature", 0.7),
                "system_message": agent.get("system_message", ""),
                "tools": agent.get("tool_names", []),
                "can_delegate": agent.get("can_delegate", True),
                "state_access": agent.get("state_access", "read_write")
            }
            
            langgraph_config["agents"].append(agent_config)
            
            # Add as node
            langgraph_config["nodes"].append({
                "id": agent_id,
                "type": "agent",
                "config": agent_config
            })
            
        # Set entry point (first agent by default)
        if langgraph_config["agents"]:
            langgraph_config["entry_point"] = langgraph_config["agents"][0]["id"]
        
        # Process tools
        for tool_name, tool_config in tools.items():
            langgraph_config["tools"][tool_name] = {
                "description": tool_config.get("description", ""),
                "config": tool_config.get("config", {}),
                "langgraph_config": {
                    "async_execution": tool_config.get("config", {}).get("use_async", False),
                    "streaming": tool_config.get("config", {}).get("streaming", False),
                    "timeout": tool_config.get("config", {}).get("timeout", 60)
                }
            }
        
        # Create edges between nodes (linear chain by default)
        for i in range(len(langgraph_config["agents"]) - 1):
            langgraph_config["edges"].append({
                "source": langgraph_config["agents"][i]["id"],
                "target": langgraph_config["agents"][i+1]["id"],
                "label": "next"
            })

        return langgraph_config
    
    async def execute_flow(
        self, 
        flow: Any, 
        input_data: Dict[str, Any],
        step_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """
        Execute a LangGraph flow with the given input data
        
        Args:
            flow: LangGraph flow configuration
            input_data: Input data for the flow
            step_callback: Optional callback for streaming updates
            
        Returns:
            Dictionary containing execution results
        """
        if not self.langgraph_available:
            raise RuntimeError("LangGraph is not installed or not properly configured")
        
        # In a production implementation, we would create a real LangGraph workflow
        # For MVP, we'll simulate the execution with proper tracing
        execution_trace = []
        
        # Extract components from the flow
        agents = flow.get("agents", [])
        tools = flow.get("tools", {})
        edges = flow.get("edges", [])
        entry_point = flow.get("entry_point")
        max_iterations = flow.get("max_iterations", 10)
        
        if not agents:
            raise ValueError("No agents defined in the flow")
            
        if not entry_point:
            if agents:
                entry_point = agents[0]["id"]
            else:
                raise ValueError("No entry point defined for the flow")
                
        # Initialize query
        query = input_data.get("query", "")
        if not query:
            raise ValueError("Input must contain a 'query' field")
            
        # Initialize state
        state = {
            "query": query,
            "conversation_history": [],
            "iteration": 0,
            "result": None,
            "_all_agents": agents
        }
        
        # Add any additional input data to the state
        for key, value in input_data.items():
            if key != "query":
                state[key] = value
                
        # Start with the entry point
        current_agent_id = entry_point
        current_step = 1
        
        try:
            # Execute the flow until max iterations or completion
            while state["iteration"] < max_iterations:
                # Find current agent
                current_agent = next((a for a in agents if a["id"] == current_agent_id), None)
                
                if not current_agent:
                    raise ValueError(f"Agent with ID {current_agent_id} not found")
                
                # Create step record for execution trace
                step_record = {
                    "step": current_step,
                    "agent_id": current_agent_id,
                    "agent_name": current_agent["name"],
                    "type": "agent_execution",
                    "input": {
                        "query": state["query"],
                        "conversation_history": state["conversation_history"]
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Simulate agent execution
                # In a real implementation, this would create a LangGraph node and execute it
                agent_response = await self._simulate_agent_execution(
                    agent=current_agent,
                    state=state,
                    tools=tools
                )
                
                # Update step record with agent response
                step_record["output"] = {
                    "content": agent_response.get("content", ""),
                    "metadata": {
                        "model": f"{current_agent['model_provider']}/{current_agent['model_name']}"
                    }
                }
                
                # Add to execution trace
                execution_trace.append(step_record)
                
                # Notify callback if provided
                if step_callback:
                    await step_callback(step_record)
                
                # Increment step counter
                current_step += 1
                
                # Add to conversation history
                state["conversation_history"].append({
                    "role": "agent",
                    "name": current_agent["name"],
                    "content": agent_response.get("content", "")
                })
                
                # Check if agent wants to use a tool
                if agent_response.get("use_tool"):
                    tool_name = agent_response.get("tool_name")
                    tool_input = agent_response.get("tool_input", {})
                    
                    # Check if tool exists and agent has access to it
                    agent_tools = current_agent.get("tools", [])
                    if tool_name in tools and tool_name in agent_tools:
                        # Create tool step record
                        tool_step = {
                            "step": current_step,
                            "agent_id": current_agent_id,
                            "agent_name": current_agent["name"],
                            "type": "tool_execution",
                            "input": tool_input,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        # Simulate tool execution
                        tool_result = await self._simulate_tool_execution(
                            tool_name=tool_name,
                            tool_input=tool_input,
                            tool_config=tools.get(tool_name, {})
                        )
                        
                        # Update tool step with result
                        tool_step["output"] = {
                            "content": json.dumps(tool_result),
                            "metadata": {"tool": tool_name}
                        }
                        
                        # Add to execution trace
                        execution_trace.append(tool_step)
                        
                        # Notify callback if provided
                        if step_callback:
                            await step_callback(tool_step)
                            
                        # Update state with tool result
                        state["tool_result"] = tool_result
                        
                        # Add to conversation history
                        state["conversation_history"].append({
                            "role": "tool",
                            "name": tool_name,
                            "content": json.dumps(tool_result)
                        })
                        
                        # Increment step counter
                        current_step += 1
                        
                    else:
                        # Tool not available to this agent
                        state["conversation_history"].append({
                            "role": "system",
                            "content": f"Tool '{tool_name}' is not available to this agent"
                        })
                
                # Check if agent wants to delegate to another agent
                elif agent_response.get("delegate_to"):
                    next_agent_id = agent_response.get("delegate_to")
                    delegation_reason = agent_response.get("delegation_reason", "")
                    
                    # Check if agent can delegate
                    if current_agent.get("can_delegate", True):
                        # Create delegation step
                        delegation_step = {
                            "step": current_step,
                            "agent_id": current_agent_id,
                            "agent_name": current_agent["name"],
                            "type": "delegation",
                            "decision": {
                                "action": "delegate",
                                "target": next_agent_id,
                                "reasoning": delegation_reason
                            },
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        # Add to execution trace
                        execution_trace.append(delegation_step)
                        
                        # Notify callback if provided
                        if step_callback:
                            await step_callback(delegation_step)
                            
                        # Update current agent
                        current_agent_id = next_agent_id
                        
                        # Add to conversation history
                        state["conversation_history"].append({
                            "role": "system",
                            "content": f"Delegating to {next_agent_id}: {delegation_reason}"
                        })
                        
                        # Increment step counter
                        current_step += 1
                        
                    else:
                        # Agent cannot delegate
                        state["conversation_history"].append({
                            "role": "system",
                            "content": f"Agent {current_agent['name']} cannot delegate to other agents"
                        })
                
                # Check if agent has a final answer
                elif agent_response.get("final_answer"):
                    state["result"] = agent_response.get("final_answer")
                    
                    # Add completion step
                    completion_step = {
                        "step": current_step,
                        "agent_id": current_agent_id,
                        "agent_name": current_agent["name"],
                        "type": "complete",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Add to execution trace
                    execution_trace.append(completion_step)
                    
                    # Notify callback if provided
                    if step_callback:
                        await step_callback(completion_step)
                        
                    # Exit the loop
                    break
                        
                # Otherwise follow the graph to the next agent (if defined)
                else:
                    # Find edge from current agent
                    next_edge = next((e for e in edges if e["source"] == current_agent_id), None)
                    
                    if next_edge:
                        current_agent_id = next_edge["target"]
                    else:
                        # No next agent defined, use the final response as result
                        state["result"] = agent_response.get("content")
                        
                        # Add completion step
                        completion_step = {
                            "step": current_step,
                            "agent_id": current_agent_id,
                            "agent_name": current_agent["name"],
                            "type": "complete",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        # Add to execution trace
                        execution_trace.append(completion_step)
                        
                        # Notify callback if provided
                        if step_callback:
                            await step_callback(completion_step)
                        
                        # Exit the loop
                        break
                
                # Increment iteration counter
                state["iteration"] += 1
                
            # If we exit the loop without a result, use the last agent's response
            if not state.get("result") and state.get("conversation_history"):
                last_agent_message = next(
                    (msg["content"] for msg in reversed(state["conversation_history"]) 
                     if msg["role"] == "agent"),
                    "No definitive result produced."
                )
                state["result"] = last_agent_message
                
            # Build the final result
            result = {
                "output": {
                    "content": state.get("result", "No result produced"),
                    "metadata": {
                        "framework": "langgraph",
                        "iterations": state["iteration"]
                    }
                },
                "execution_trace": execution_trace,
                "steps": len(execution_trace)
            }
            
            return result
            
        except Exception as e:
            logger.exception(f"Error executing LangGraph flow: {str(e)}")
            
            # Create error step
            error_step = {
                "step": current_step,
                "type": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to execution trace
            execution_trace.append(error_step)
            
            # Return error result
            return {
                "output": {
                    "error": str(e),
                    "metadata": {
                        "framework": "langgraph",
                        "iterations": state["iteration"]
                    }
                },
                "execution_trace": execution_trace,
                "steps": len(execution_trace)
            }
    
    async def _simulate_agent_execution(
        self, 
        agent: Dict[str, Any], 
        state: Dict[str, Any],
        tools: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate LangGraph agent execution for the MVP
        In a real implementation, this would create a LangGraph node and execute it
        
        Args:
            agent: Agent configuration
            state: Current state
            tools: Available tools
            
        Returns:
            Simulated agent response
        """
        # For the MVP, we'll return a simulated response
        # In production, this would use LangGraph to create and run a node
        
        # Simplified logic for the simulation (can be expanded later)
        query = state.get("query", "")
        iteration = state.get("iteration", 0)
        agent_name = agent.get("name", "Agent")
        agent_tools = agent.get("tools", [])
        
        # Simulate some processing time
        await asyncio.sleep(0.5)
        
        if iteration == 0:
            # First iteration - agent introduction
            return {
                "content": f"I am {agent_name}. I will help with: {query}",
                "use_tool": len(agent_tools) > 0 and "web_search" in agent_tools,
                "tool_name": "web_search" if "web_search" in agent_tools else None,
                "tool_input": {"query": query} if "web_search" in agent_tools else None
            }
        elif "tool_result" in state:
            # Process tool results
            tool_result = state.get("tool_result", {})
            
            if iteration >= 3:
                # Final answer after processing enough information
                return {
                    "content": f"Based on my analysis of {query}, I have found the information.",
                    "final_answer": f"Based on my analysis as {agent_name}, here's what I found about '{query}': [simulated final response based on the tool results and agent expertise]"
                }
            else:
                # Continue processing or delegate
                other_agents = [a for a in state.get("_all_agents", []) if a["id"] != agent.get("id")]
                
                if other_agents and iteration == 1:
                    # Delegate to another agent
                    next_agent = other_agents[0]
                    return {
                        "content": f"I'll delegate this to {next_agent['name']} for further analysis.",
                        "delegate_to": next_agent["id"],
                        "delegation_reason": f"Need specialized expertise from {next_agent['name']}"
                    }
                else:
                    # Use another tool if available
                    if "data_analysis" in agent_tools:
                        return {
                            "content": f"I'll analyze the results more deeply.",
                            "use_tool": True,
                            "tool_name": "data_analysis",
                            "tool_input": {"data": tool_result, "analysis_type": "exploratory"}
                        }
                    else:
                        # No other tools to use, provide an answer
                        return {
                            "content": f"Here's what I found about '{query}'.",
                            "final_answer": f"Based on my research as {agent_name}, I've found information about '{query}': [simulated response based on {agent_name}'s expertise]"
                        }
        else:
            # Generic response
            return {
                "content": f"I'm continuing to work on '{query}'.",
                "final_answer": f"After thorough analysis as {agent_name}, I can provide this information about '{query}': [simulated final response from {agent_name}]"
            }
    
    async def _simulate_tool_execution(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate tool execution for the MVP
        In a real implementation, this would call the actual tool
        
        Args:
            tool_name: Name of the tool to execute
            tool_input: Input for the tool
            tool_config: Tool configuration
            
        Returns:
            Simulated tool result
        """
        # For the MVP, we'll return a simulated response
        # In production, this would call the actual tool implementation
        
        # Simulate some processing time
        await asyncio.sleep(0.5)
        
        # Simplified simulation based on tool name
        if tool_name == "web_search":
            query = tool_input.get("query", "")
            return {
                "result": [
                    {
                        "title": f"Result 1 for {query}",
                        "url": "https://example.com/1",
                        "snippet": f"This is a simulated search result for {query}."
                    },
                    {
                        "title": f"Result 2 for {query}",
                        "url": "https://example.com/2",
                        "snippet": f"Another simulated result for {query} with different information."
                    }
                ],
                "query": query
            }
            
        elif tool_name == "data_analysis":
            data = tool_input.get("data", [])
            return {
                "analysis": f"Simulated analysis of provided data with {len(data)} records",
                "insights": ["Insight 1", "Insight 2", "Insight 3"],
                "summary": "This is a simulated data analysis summary."
            }
            
        elif tool_name == "code_execution":
            language = tool_input.get("language", "python")
            code = tool_input.get("code", "")
            return {
                "output": "This is simulated code execution output.\nResult: Simulated result",
                "error": None,
                "success": True
            }
            
        else:
            # Generic tool response
            return {
                "result": f"Simulated result from {tool_name}",
                "metadata": {
                    "tool": tool_name,
                    "simulated": True
                }
            }
    
    def register_tools(
        self, 
        tools: List[Dict[str, Any]], 
        framework_config: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Register tools with LangGraph
        
        Args:
            tools: List of tool configurations
            framework_config: Optional LangGraph-specific configuration
            
        Returns:
            LangGraph-specific tool configuration
        """
        if not self.langgraph_available:
            raise RuntimeError("LangGraph is not installed or not properly configured")
            
        # For MVP, we'll create a simplified tool registry
        # In a real implementation, this would register tools with LangGraph
        
        registered_tools = {}
        
        for tool in tools:
            tool_name = tool.get("name")
            if not tool_name:
                continue
                
            # Extract LangGraph specific configuration
            langgraph_config = tool.get("config", {})
            use_async = langgraph_config.get("use_async", False)
            streaming = langgraph_config.get("streaming", False)
            timeout = langgraph_config.get("timeout", 60)
            
            # Create LangGraph tool configuration
            registered_tools[tool_name] = {
                "description": tool.get("description", ""),
                "parameters": tool.get("parameters", {}),
                "langgraph_config": {
                    "async_execution": use_async,
                    "streaming": streaming,
                    "timeout": timeout
                },
                "function_name": tool.get("function_name")
            }
        
        return {
            "registered_tools": registered_tools,
            "framework": "langgraph"
        }
        
    def get_supported_features(self) -> Dict[str, bool]:
        """Return features supported by LangGraph"""
        return {
            "multi_agent": True,
            "parallel_execution": True,
            "tools": True,
            "streaming": True,
            "visualization": True
        }
        
    def validate_flow(self, flow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a flow configuration for LangGraph
        
        Args:
            flow_config: Flow configuration to validate
            
        Returns:
            Dictionary with validation results
        """
        # Start with basic validation from parent class
        validation_result = super().validate_flow(flow_config)
        
        # Additional LangGraph-specific validations
        agents = flow_config.get("agents", [])
        
        # Check for valid model providers
        for i, agent in enumerate(agents):
            provider = agent.get("model_provider", "")
            if provider and provider not in ["openai", "anthropic", "google", "vertex_ai", "azure"]:
                validation_result["warnings"].append(
                    f"Agent {i+1}: Model provider '{provider}' may not be fully compatible with LangGraph"
                )
                
        # Check for tool configuration
        tools = flow_config.get("tools", {})
        for tool_name, tool_config in tools.items():
            config = tool_config.get("config", {})
            if config.get("use_async") and not self.has_full_imports:
                validation_result["warnings"].append(
                    f"Tool '{tool_name}': Async execution requires additional LangGraph components"
                )
                
        return validation_result
        
    def get_default_agent_config(self) -> Dict[str, Any]:
        """Get default configuration for a LangGraph agent"""
        return {
            "name": "Default LangGraph Agent",
            "description": "Default agent for LangGraph flows",
            "model_provider": "openai",
            "model_name": "gpt-4",
            "temperature": 0.7,
            "system_message": "You are a helpful AI assistant working as part of a LangGraph workflow.",
            "capabilities": ["reasoning"],
            "tool_names": [],
            "state_access": "read_write"  # LangGraph specific
        }
        
    async def visualize_flow(
        self, 
        flow: Any, 
        format: str = "json",
        include_tools: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a LangGraph-specific visualization of the flow
        
        Args:
            flow: LangGraph flow object
            format: Desired format ('json', 'mermaid', 'dot')
            include_tools: Whether to include tool nodes
            
        Returns:
            Dictionary containing visualization data
        """
        # Extract components from the flow
        agents = flow.get("agents", [])
        tools = flow.get("tools", {})
        edges = flow.get("edges", [])
        
        # Prepare nodes and connections
        nodes = []
        connections = []
        
        # Add agent nodes
        for agent in agents:
            nodes.append({
                "id": agent["id"],
                "name": agent["name"],
                "type": "agent",
                "agent_type": "langgraph",
                "model": f"{agent['model_provider']}/{agent['model_name']}",
                "tools": agent.get("tools", [])
            })
            
        # Add connections from edges
        for edge in edges:
            connections.append({
                "source": edge["source"],
                "target": edge["target"],
                "label": edge.get("label", "next"),
                "type": "flow"
            })
            
        # Add tool nodes if requested
        if include_tools:
            for tool_name, tool_config in tools.items():
                tool_id = f"tool-{tool_name}"
                nodes.append({
                    "id": tool_id,
                    "name": tool_name,
                    "type": "tool",
                    "description": tool_config.get("description", "")
                })
                
                # Add connections from agents to tools
                for agent in agents:
                    if tool_name in agent.get("tools", []):
                        connections.append({
                            "source": agent["id"],
                            "target": tool_id,
                            "type": "tool",
                            "bidirectional": True
                        })
        
        # Format output based on requested format
        if format == "mermaid":
            mermaid_output = self._generate_mermaid(nodes, connections)
            return {
                "nodes": nodes,
                "edges": connections,
                "framework": "langgraph",
                "format": "mermaid",
                "mermaid": mermaid_output
            }
        elif format == "dot":
            dot_output = self._generate_dot(nodes, connections)
            return {
                "nodes": nodes,
                "edges": connections,
                "framework": "langgraph",
                "format": "dot",
                "dot": dot_output
            }
        else:
            # Default JSON format
            return {
                "nodes": nodes,
                "edges": connections,
                "framework": "langgraph",
                "format": "json"
            }
            
    def _generate_mermaid(self, nodes: List[Dict[str, Any]], connections: List[Dict[str, Any]]) -> str:
        """Generate Mermaid diagram for the flow"""
        mermaid = ["graph TD;"]
        
        # Add nodes
        for node in nodes:
            node_id = node["id"]
            node_name = node["name"]
            node_type = node["type"]
            
            # Style based on node type
            if node_type == "agent":
                mermaid.append(f'  {node_id}["{node_name}"] class agentStyle;')
            elif node_type == "tool":
                mermaid.append(f'  {node_id}["{node_name}"] class toolStyle;')
            else:
                mermaid.append(f'  {node_id}["{node_name}"];')
                
        # Add connections
        for conn in connections:
            source = conn["source"]
            target = conn["target"]
            label = conn.get("label", "")
            
            if conn.get("bidirectional"):
                mermaid.append(f'  {source} <--> {target};')
            else:
                if label:
                    mermaid.append(f'  {source} -->|"{label}"| {target};')
                else:
                    mermaid.append(f'  {source} --> {target};')
                
        # Add styles
        mermaid.append("  classDef agentStyle fill:#D6EAF8,stroke:#3498DB,color:#000;")
        mermaid.append("  classDef toolStyle fill:#FCF3CF,stroke:#F1C40F,color:#000;")
        
        return "\n".join(mermaid)
        
    def _generate_dot(self, nodes: List[Dict[str, Any]], connections: List[Dict[str, Any]]) -> str:
        """Generate DOT (GraphViz) diagram for the flow"""
        dot = ["digraph G {"]
        dot.append("  rankdir=TD;")
        dot.append("  node [shape=box, style=rounded, fontname=Arial];")
        
        # Add nodes
        for node in nodes:
            node_id = node["id"]
            node_name = node["name"]
            node_type = node["type"]
            
            # Style based on node type
            if node_type == "agent":
                dot.append(f'  "{node_id}" [label="{node_name}", fillcolor="#D6EAF8", style="filled,rounded", color="#3498DB"];')
            elif node_type == "tool":
                dot.append(f'  "{node_id}" [label="{node_name}", fillcolor="#FCF3CF", style="filled,rounded", color="#F1C40F"];')
            else:
                dot.append(f'  "{node_id}" [label="{node_name}"];')
                
        # Add connections
        for conn in connections:
            source = conn["source"]
            target = conn["target"]
            label = conn.get("label", "")
            
            if conn.get("bidirectional"):
                dot.append(f'  "{source}" -> "{target}" [dir=both, label="{label}"];')
            else:
                dot.append(f'  "{source}" -> "{target}" [label="{label}"];')
                
        dot.append("}")
        
        return "\n".join(dot)
