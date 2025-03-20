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
            from langchain.graphs import Graph
            self.Graph = Graph
            
            # Check if we have LangGraph components
            try:
                from langchain_experimental import pydantic_v1
                from langchain.agents import AgentExecutor, tool
                self.AgentExecutor = AgentExecutor
                self.tool_decorator = tool
                self.has_full_imports = True
            except ImportError:
                self.has_full_imports = False
                logger.warning("LangGraph agent components not available")
                
        except ImportError:
            self.langgraph_available = False
            logger.warning("LangGraph not installed - some functionality may be limited")
            
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
                mermaid.append(f'  {node_id}["{node_name}"] classDef agentStyle;')
            elif node_type == "tool":
                mermaid.append(f'  {node_id}["{node_name}"] classDef toolStyle;')
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

_input,
                            tool_config=tools.get(tool_name, {})
                        )
                        
                        # Update tool step with result
                        tool_step["output"] = {
                            "content": tool_result.get("result", "No result"),
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
                            "agent_id": current_agent["id"],
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
                        "agent_id": current_agent["id"],
                        "agent_name": current_agent["name"],
                        "type": "complete",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Add to execution trace
                    execution_trace.append(completion_step)
                    
                    # Notify callback if provided
                    if step_callback:
                        await step_callback(completion_step)
                        
                # Otherwise follow the graph to the next agent (if defined)
                else:
                    # Find edge from current agent
                    edges = flow.get("edges", [])
                    next_edge = next((e for e in edges if e["source"] == current_agent_id), None)
                    
                    if next_edge:
                        current_agent_id = next_edge["target"]
                    else:
                        # No next agent defined, use the final response as result
                        state["result"] = agent_response.get("content")
                
                # Increment iteration counter
                state["iteration"] += 1
                
            # If we exit the loop without a result, use the last agent's response
            if not state.get("result") and state.get("conversation_history"):
                state["result"] = "No definitive result was produced after {state['iteration']} iterations."
                
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


                "
