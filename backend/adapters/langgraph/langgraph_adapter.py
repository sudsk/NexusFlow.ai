# backend/adapters/langgraph/langgraph_adapter.py
from typing import Dict, List, Any, Optional, Callable, Awaitable, Union
import asyncio
import logging
import json
import importlib
import inspect
from datetime import datetime
import uuid

from ...adapters.interfaces.base_adapter import FrameworkAdapter

logger = logging.getLogger(__name__)

class LangGraphAdapter(FrameworkAdapter):
    """Adapter for LangGraph framework"""

    def __init__(self):
        # Check if langgraph is installed
        try:
            self.langgraph_available = True
            import langchain
            self.langchain_version = getattr(langchain, '__version__', 'unknown')
            
            # Import LangGraph modules
            try:
                import langgraph
                self.langgraph_version = getattr(langgraph, '__version__', 'unknown')
                
                from langgraph.graph import StateGraph
                self.Graph = StateGraph
                
                # Import LangChain components
                from langchain.schema import AgentAction, AgentFinish
                from langchain_core.messages import (
                    AIMessage, 
                    HumanMessage, 
                    SystemMessage, 
                    ChatMessage, 
                    FunctionMessage
                )
                from langchain.agents import AgentExecutor
                from langchain.tools import Tool
                from langchain_openai import ChatOpenAI
                from langchain_anthropic import ChatAnthropic
                
                # Store imported components
                self.AgentAction = AgentAction
                self.AgentFinish = AgentFinish
                self.AIMessage = AIMessage
                self.HumanMessage = HumanMessage
                self.SystemMessage = SystemMessage
                self.ChatMessage = ChatMessage
                self.FunctionMessage = FunctionMessage
                self.AgentExecutor = AgentExecutor
                self.Tool = Tool
                self.ChatOpenAI = ChatOpenAI
                self.ChatAnthropic = ChatAnthropic
                
                self.has_full_imports = True
                logger.info(f"LangGraph adapter initialized with version {self.langgraph_version}")
                
            except ImportError as e:
                logger.warning(f"LangGraph modules not fully available: {str(e)}")
                self.langgraph_available = False
                self.has_full_imports = False
                    
        except ImportError:
            self.langgraph_available = False
            logger.warning("LangGraph not installed - some functionality may be limited")
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
        if not self.langgraph_available or not self.has_full_imports:
            raise RuntimeError("LangGraph is not installed or not properly configured")
        
        # Extract components from the flow
        agents_config = flow.get("agents", [])
        tools_config = flow.get("tools", {})
        edges = flow.get("edges", [])
        entry_point = flow.get("entry_point")
        max_iterations = flow.get("max_iterations", 10)
        
        if not agents_config:
            raise ValueError("No agents defined in the flow")
            
        if not entry_point:
            if agents_config:
                entry_point = agents_config[0]["id"]
            else:
                raise ValueError("No entry point defined for the flow")
                
        # Initialize execution trace
        execution_trace = []
        current_step = 1
        
        # Initialize query from input data
        query = input_data.get("query", "")
        if not query:
            raise ValueError("Input must contain a 'query' field")
        
        try:
            # Create the LangGraph state definition
            state_dict = {
                "keys": ["query", "conversation_history", "current_agent", "tool_calls", "final_answer"],
                "query": query,
                "conversation_history": [],
                "current_agent": entry_point,
                "tool_calls": [],
                "final_answer": None
            }
            
            # Create a dictionary of tools available to agents
            tools_registry = await self._build_tools_registry(tools_config)
            
            # Create agent LLM instances
            agent_llms = {}
            for agent_config in agents_config:
                agent_id = agent_config["id"]
                model_provider = agent_config["model_provider"]
                model_name = agent_config["model_name"]
                temperature = agent_config.get("temperature", 0.7)
                
                # Create the LLM based on provider
                if model_provider == "openai":
                    agent_llms[agent_id] = self.ChatOpenAI(
                        model=model_name,
                        temperature=temperature
                    )
                elif model_provider == "anthropic":
                    agent_llms[agent_id] = self.ChatAnthropic(
                        model=model_name,
                        temperature=temperature
                    )
                else:
                    # Default to OpenAI
                    agent_llms[agent_id] = self.ChatOpenAI(
                        model=model_name,
                        temperature=temperature
                    )
            
            # Build a graph of agent nodes
            graph = self.Graph()
            
            # Define node functions for each agent
            for agent_config in agents_config:
                agent_id = agent_config["id"]
                agent_name = agent_config["name"]
                agent_system_message = agent_config["system_message"]
                agent_tools = agent_config["tools"]
                
                # Create a list of available tools for this agent
                agent_tool_objects = []
                for tool_name in agent_tools:
                    if tool_name in tools_registry:
                        agent_tool_objects.append(tools_registry[tool_name])
                
                # Create a node function for this agent
                agent_node_fn = self._create_agent_node_function(
                    agent_id=agent_id,
                    agent_name=agent_name,
                    agent_llm=agent_llms.get(agent_id),
                    system_message=agent_system_message,
                    tools=agent_tool_objects,
                    step_callback=step_callback,
                    execution_trace=execution_trace,
                    current_step_ref=[current_step]  # Pass as a mutable reference
                )
                
                # Add the node to the graph
                graph.add_node(agent_id, agent_node_fn)
            
            # Add conditional edges based on the config
            for agent_config in agents_config:
                agent_id = agent_config["id"]
                can_delegate = agent_config.get("can_delegate", True)
                
                if can_delegate:
                    # Define a router function that decides the next agent
                    graph.add_conditional_edges(
                        agent_id,
                        self._create_router_function(agents_config)
                    )
                else:
                    # Find static edge if any
                    next_agent = None
                    for edge in edges:
                        if edge["source"] == agent_id:
                            next_agent = edge["target"]
                            break
                    
                    if next_agent:
                        graph.add_edge(agent_id, next_agent)
            
            # Set entry point
            graph.set_entry_point(entry_point)
            
            # Define state for final answer
            graph.set_finish_point("final_answer")
            
            # Compile the graph into a runnable
            runnable = graph.compile()
            
            # Execute the graph
            for step in runnable.stream({
                "query": query,
                "conversation_history": [],
                "current_agent": entry_point,
                "tool_calls": [],
                "final_answer": None
            }):
                # The streaming provides state updates as the graph executes
                logger.debug(f"Stream update: {step}")
                
                # Check if we reached final answer
                if step.get("final_answer"):
                    break
                    
                # Check for max iterations to prevent infinite loops
                if current_step > max_iterations * 3:  # Each agent step may include multiple operations
                    # Add a step indicating we hit the iteration limit
                    limit_step = {
                        "step": current_step,
                        "type": "limit_reached",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    execution_trace.append(limit_step)
                    
                    # Notify callback if provided
                    if step_callback:
                        await step_callback(limit_step)
                        
                    break
            
            # Get the final state
            final_state = step  # Last state from the stream
            
            # Add completion step
            completion_step = {
                "step": current_step,
                "type": "complete",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to execution trace
            execution_trace.append(completion_step)
            
            # Notify callback if provided
            if step_callback:
                await step_callback(completion_step)
                
            # Extract the final answer
            final_answer = final_state.get("final_answer")
            if not final_answer and final_state.get("conversation_history"):
                # Try to get the last agent message as final answer
                for msg in reversed(final_state.get("conversation_history", [])):
                    if msg.get("role") == "agent":
                        final_answer = msg.get("content")
                        break
            
            # Build the final result
            result = {
                "output": {
                    "content": final_answer or "No definitive result produced.",
                    "metadata": {
                        "framework": "langgraph",
                        "iterations": current_step - 1
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
                        "iterations": current_step
                    }
                },
                "execution_trace": execution_trace,
                "steps": len(execution_trace)
            }
    
    def _create_agent_node_function(
        self, 
        agent_id: str, 
        agent_name: str,
        agent_llm: Any,
        system_message: str,
        tools: List[Any],
        step_callback: Optional[Callable],
        execution_trace: List[Dict[str, Any]],
        current_step_ref: List[int]
    ):
        """
        Create a node function for a LangGraph agent
        
        Args:
            agent_id: ID of the agent
            agent_name: Name of the agent
            agent_llm: LLM instance for the agent
            system_message: System message for the agent
            tools: List of tools available to the agent
            step_callback: Callback for streaming steps
            execution_trace: Execution trace to append steps to
            current_step_ref: Mutable reference to current step counter
            
        Returns:
            Node function for LangGraph
        """
        async def agent_fn(state):
            # Get current step number
            current_step = current_step_ref[0]
            
            # Extract state values
            query = state["query"]
            conversation_history = state["conversation_history"]
            current_agent = state["current_agent"]
            tool_calls = state["tool_calls"]
            
            # Only proceed if this agent is the current agent
            if current_agent != agent_id:
                return state
            
            # Add a step for agent execution
            step_record = {
                "step": current_step,
                "agent_id": agent_id,
                "agent_name": agent_name,
                "type": "agent_execution",
                "input": {
                    "query": query,
                    "conversation_history": conversation_history
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Prepare messages for the agent
            messages = []
            
            # Add system message
            if system_message:
                messages.append(self.SystemMessage(content=system_message))
                
            # Add initial query if this is the first interaction
            if not conversation_history:
                messages.append(self.HumanMessage(content=query))
            else:
                # Add conversation history
                for msg in conversation_history:
                    if msg["role"] == "human":
                        messages.append(self.HumanMessage(content=msg["content"]))
                    elif msg["role"] == "agent":
                        messages.append(self.AIMessage(content=msg["content"]))
                    elif msg["role"] == "system":
                        messages.append(self.SystemMessage(content=msg["content"]))
                    elif msg["role"] == "tool":
                        messages.append(self.FunctionMessage(
                            name=msg.get("name", "tool"),
                            content=msg["content"]
                        ))
            
            try:
                # Get response from the agent
                response = await agent_llm.ainvoke(messages)
                
                # Extract content from response
                content = response.content
                
                # Update step record with agent response
                step_record["output"] = {
                    "content": content,
                    "metadata": {
                        "model": f"{agent_llm.model}"
                    }
                }
                
                # Add to execution trace
                execution_trace.append(step_record)
                
                # Notify callback if provided
                if step_callback:
                    await step_callback(step_record)
                
                # Increment step counter
                current_step_ref[0] += 1
                
                # Add to conversation history
                conversation_history.append({
                    "role": "agent",
                    "name": agent_name,
                    "content": content
                })
                
                # Check if the agent wants to use a tool
                if tools and any(tool_name.lower() in content.lower() for tool in tools for tool_name in [tool.name]):
                    # Simple tool detection for MVP - in production use proper tool parsing
                    for tool in tools:
                        if tool.name.lower() in content.lower():
                            # Extract tool input from content (simple regex)
                            import re
                            tool_input_match = re.search(r'{.*}', content)
                            tool_input = {}
                            
                            if tool_input_match:
                                try:
                                    tool_input = json.loads(tool_input_match.group(0))
                                except json.JSONDecodeError:
                                    tool_input = {"query": query}
                            else:
                                tool_input = {"query": query}
                            
                            # Create tool step record
                            tool_step = {
                                "step": current_step_ref[0],
                                "agent_id": agent_id,
                                "agent_name": agent_name,
                                "type": "tool_execution",
                                "input": tool_input,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                            
                            try:
                                # Execute the tool
                                tool_result = await tool.ainvoke(tool_input)
                                
                                # Update tool step with result
                                tool_step["output"] = {
                                    "content": json.dumps(tool_result) if isinstance(tool_result, dict) else str(tool_result),
                                    "metadata": {"tool": tool.name}
                                }
                                
                                # Add to execution trace
                                execution_trace.append(tool_step)
                                
                                # Notify callback if provided
                                if step_callback:
                                    await step_callback(tool_step)
                                    
                                # Update state with tool result
                                tool_calls.append({
                                    "tool": tool.name,
                                    "input": tool_input,
                                    "output": tool_result
                                })
                                
                                # Add to conversation history
                                conversation_history.append({
                                    "role": "tool",
                                    "name": tool.name,
                                    "content": json.dumps(tool_result) if isinstance(tool_result, dict) else str(tool_result)
                                })
                                
                                # Increment step counter
                                current_step_ref[0] += 1
                                
                            except Exception as e:
                                # Handle tool execution error
                                tool_step["output"] = {
                                    "error": str(e),
                                    "metadata": {"tool": tool.name}
                                }
                                
                                # Add to execution trace
                                execution_trace.append(tool_step)
                                
                                # Notify callback if provided
                                if step_callback:
                                    await step_callback(tool_step)
                                    
                                # Add to conversation history
                                conversation_history.append({
                                    "role": "system",
                                    "content": f"Error executing tool {tool.name}: {str(e)}"
                                })
                                
                                # Increment step counter
                                current_step_ref[0] += 1
                            
                            break  # Use the first matching tool
                
                # Check if agent wants to delegate
                elif "delegate to" in content.lower() or "hand off to" in content.lower():
                    # Simple delegation detection
                    import re
                    delegate_match = re.search(r'delegate to (\w+[-\w+]*)', content.lower())
                    if not delegate_match:
                        delegate_match = re.search(r'hand off to (\w+[-\w+]*)', content.lower())
                        
                    if delegate_match:
                        next_agent_id = delegate_match.group(1)
                        
                        # Create delegation step
                        delegation_step = {
                            "step": current_step_ref[0],
                            "agent_id": agent_id,
                            "agent_name": agent_name,
                            "type": "delegation",
                            "decision": {
                                "action": "delegate",
                                "target": next_agent_id,
                                "reasoning": content
                            },
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        # Add to execution trace
                        execution_trace.append(delegation_step)
                        
                        # Notify callback if provided
                        if step_callback:
                            await step_callback(delegation_step)
                            
                        # Update state
                        state["current_agent"] = next_agent_id
                        
                        # Add to conversation history
                        conversation_history.append({
                            "role": "system",
                            "content": f"Delegating to {next_agent_id}: {content}"
                        })
                        
                        # Increment step counter
                        current_step_ref[0] += 1
                
                # Check for final answer marker
                elif "final answer:" in content.lower() or "final response:" in content.lower():
                    # Extract final answer
                    final_answer_parts = content.split("Final Answer:", 1) if "Final Answer:" in content else content.split("final answer:", 1)
                    
                    if len(final_answer_parts) > 1:
                        final_answer = final_answer_parts[1].strip()
                    else:
                        final_answer = content
                        
                    # Create final answer step
                    final_step = {
                        "step": current_step_ref[0],
                        "agent_id": agent_id,
                        "agent_name": agent_name,
                        "type": "final_answer",
                        "output": {
                            "content": final_answer
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Add to execution trace
                    execution_trace.append(final_step)
                    
                    # Notify callback if provided
                    if step_callback:
                        await step_callback(final_step)
                        
                    # Set final answer in state
                    state["final_answer"] = final_answer
                    
                    # Increment step counter
                    current_step_ref[0] += 1
                    
                # Update state with conversation history
                state["conversation_history"] = conversation_history
                
                return state
                
            except Exception as e:
                logger.exception(f"Error in agent node function: {str(e)}")
                
                # Update step with error
                step_record["output"] = {
                    "error": str(e),
                    "metadata": {
                        "model": f"{agent_llm.model}"
                    }
                }
                
                # Add to execution trace
                execution_trace.append(step_record)
                
                # Notify callback if provided
                if step_callback:
                    await step_callback(step_record)
                    
                # Increment step counter
                current_step_ref[0] += 1
                
                # Add to conversation history
                conversation_history.append({
                    "role": "system",
                    "content": f"Error in agent execution: {str(e)}"
                })
                
                # Update state
                state["conversation_history"] = conversation_history
                
                return state
        
        # Return the node function
        return agent_fn
    
    def _create_router_function(self, agents_config: List[Dict[str, Any]]):
        """
        Create a router function that determines the next agent based on state
        
        Args:
            agents_config: List of agent configurations
            
        Returns:
            Router function for conditional edges
        """
        def router(state):
            # Get the current agent from state
            current_agent = state.get("current_agent")
            
            # Check if there's a delegation
            for msg in reversed(state.get("conversation_history", [])):
                if msg.get("role") == "system" and "delegating to" in msg.get("content", "").lower():
                    # Extract the agent ID from the message
                    import re
                    match = re.search(r"delegating to (\w+[-\w+]*)", msg.get("content", "").lower())
                    if match:
                        next_agent = match.group(1)
                        # Verify the agent exists
                        if any(agent["id"] == next_agent for agent in agents_config):
                            return next_agent
            
            # Check if there's a final answer
            if state.get("final_answer"):
                return "final_answer"
                
            # Default: continue with the current agent
            return current_agent
            
        return router
    
    async def _build_tools_registry(self, tools_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a registry of tool objects for use in the LangGraph execution
        
        Args:
            tools_config: Tool configurations from the flow
            
        Returns:
            Dictionary of tool objects keyed by name
        """
        from ...services.tool.registry_service import get_tool_registry
        tool_registry = get_tool_registry()
        
        tools = {}
        
        for tool_name, tool_config in tools_config.items():
            # Create a Tool object for each configured tool
            description = tool_config.get("description", "")
            
            # Create the Tool using LangChain's Tool class
            tools[tool_name] = self.Tool(
                name=tool_name,
                description=description,
                func=lambda **kwargs, tool_name=tool_name: self._execute_tool(tool_name, kwargs),
                coroutine=lambda **kwargs, tool_name=tool_name: self._execute_tool_async(tool_name, kwargs)
            )
            
        return tools
    
    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronous wrapper for tool execution
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            
        Returns:
            Tool execution result
        """
        # Get event loop
        loop = asyncio.get_event_loop()
        
        # Run the async function in the event loop
        return loop.run_until_complete(self._execute_tool_async(tool_name, parameters))
    
    async def _execute_tool_async(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool using the tool registry
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            
        Returns:
            Tool execution result
        """
        from ...services.tool.registry_service import get_tool_registry
        tool_registry = get_tool_registry()
        
        try:
            # Execute the tool through the registry
            result = await tool_registry.execute_tool(tool_name, parameters)
            return result
        except Exception as e:
            logger.exception(f"Error executing tool {tool_name}: {str(e)}")
            return {
                "error": str(e),
                "tool": tool_name,
                "status": "error"
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
