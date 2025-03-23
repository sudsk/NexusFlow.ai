# backend/adapters/langgraph/langgraph_adapter.py
from typing import Dict, List, Any, Optional, Callable, Awaitable, Union
import asyncio
import logging
import json
import importlib
import inspect
from datetime import datetime
from typing import TypedDict, Annotated, List, Dict, Any, Optional

# Pydantic for state management
from pydantic import BaseModel, Field

# LangChain and LangGraph imports
from langchain_core.messages import (
    AIMessage, 
    HumanMessage, 
    SystemMessage, 
    ChatMessage, 
    FunctionMessage
)
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from langgraph.graph import StateGraph, END
from langgraph.checkpoint import MemorySaver
from langgraph.prebuilt import tools_condition

# LLM Providers
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

# Adapter and base dependencies
from ...adapters.interfaces.base_adapter import FrameworkAdapter
from ...services.tool.registry_service import get_tool_registry

# Configure logging
logger = logging.getLogger(__name__)

class LangGraphAdapter(FrameworkAdapter):
    """Advanced adapter for LangGraph framework with comprehensive integration"""
    
    def __init__(self):
        """Initialize the LangGraph adapter with advanced configuration"""
        # LLM provider mapping
        self.llm_providers = {
            "openai": self._create_openai_llm,
            "anthropic": self._create_anthropic_llm,
            "google": self._create_google_llm
        }
        
        # Tool registry
        self.tool_registry = get_tool_registry()
        
        # Checkpoint for maintaining conversation state
        self.checkpoint_handler = MemorySaver()
    
    def get_framework_name(self) -> str:
        """Return the framework name"""
        return "langgraph"
    
    def _create_openai_llm(self, model_name: str, temperature: float) -> BaseChatModel:
        """Create an OpenAI language model instance"""
        try:
            return ChatOpenAI(
                model=model_name, 
                temperature=temperature, 
                streaming=True
            )
        except ImportError:
            logger.error("OpenAI LLM import failed")
            raise
    
    def _create_anthropic_llm(self, model_name: str, temperature: float) -> BaseChatModel:
        """Create an Anthropic language model instance"""
        try:
            return ChatAnthropic(
                model=model_name, 
                temperature=temperature, 
                streaming=True
            )
        except ImportError:
            logger.error("Anthropic LLM import failed")
            raise
    
    def _create_google_llm(self, model_name: str, temperature: float) -> BaseChatModel:
        """Create a Google language model instance"""
        try:
            return ChatGoogleGenerativeAI(
                model=model_name, 
                temperature=temperature, 
                streaming=True
            )
        except ImportError:
            logger.error("Google LLM import failed")
            raise
    
    def _create_llm(self, agent_config: Dict[str, Any]) -> BaseChatModel:
        """
        Create a language model based on provider configuration
        
        Args:
            agent_config: Configuration dictionary for the agent
        
        Returns:
            Instantiated language model
        """
        provider = agent_config.get("model_provider", "openai").lower()
        model_name = agent_config.get("model_name", "gpt-4")
        temperature = agent_config.get("temperature", 0.7)
        
        # Select provider function
        provider_func = self.llm_providers.get(provider)
        if not provider_func:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        
        return provider_func(model_name, temperature)
    
    def _create_tools(self, tool_names: List[str]) -> List[BaseTool]:
        """
        Create tool instances for an agent
        
        Args:
            tool_names: List of tool names to instantiate
        
        Returns:
            List of tool objects
        """
        tools = []
        for tool_name in tool_names:
            try:
                # Get tool configuration from registry
                tool_config = self.tool_registry.get_tool(tool_name)
                if not tool_config:
                    logger.warning(f"Tool {tool_name} not found in registry")
                    continue
                
                # Execute tool through registry to get the actual function
                async def tool_wrapper(params):
                    return await self.tool_registry.execute_tool(tool_name, params)
                
                # Wrap the tool in a BaseTool compatible interface
                tool = BaseTool(
                    name=tool_name,
                    description=tool_config.get("description", ""),
                    func=tool_wrapper
                )
                tools.append(tool)
                
            except Exception as e:
                logger.error(f"Error creating tool {tool_name}: {str(e)}")
        
        return tools
    
    def convert_flow(self, flow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert NexusFlow configuration to LangGraph configuration
        
        Args:
            flow_config: Flow configuration dictionary
        
        Returns:
            LangGraph specific configuration
        """
        # Validate basic configuration
        if not flow_config.get("agents"):
            raise ValueError("Flow must have at least one agent")
        
        # Prepare flow configuration
        langgraph_config = {
            "type": "langgraph_flow",
            "agents": [],
            "tools": {},
            "state_schema": {},
            "max_iterations": flow_config.get("max_steps", 10)
        }
        
        # Process tools
        for tool_name, tool_config in flow_config.get("tools", {}).items():
            langgraph_config["tools"][tool_name] = {
                "description": tool_config.get("description", ""),
                "config": tool_config.get("config", {})
            }
        
        # Process agents
        for agent_config in flow_config.get("agents", []):
            agent_entry = {
                "id": agent_config.get("agent_id", f"agent-{len(langgraph_config['agents'])}"),
                "name": agent_config.get("name", "Unnamed Agent"),
                "model_provider": agent_config.get("model_provider", "openai"),
                "model_name": agent_config.get("model_name", "gpt-4"),
                "temperature": agent_config.get("temperature", 0.7),
                "system_message": agent_config.get("system_message", ""),
                "tools": agent_config.get("tool_names", [])
            }
            
            langgraph_config["agents"].append(agent_entry)
        
        return langgraph_config
    
    async def execute_flow(
        self, 
        flow: Dict[str, Any], 
        input_data: Dict[str, Any],
        step_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """
        Execute a LangGraph flow
        
        Args:
            flow: LangGraph flow configuration
            input_data: Input data for the flow
            step_callback: Optional callback for streaming updates
            
        Returns:
            Execution result dictionary
        """
        try:
            # Create Pydantic state schema dynamically
            class GraphState(BaseModel):
                """Dynamic state schema for the flow"""
                query: str = Field(description="Main query or input")
                conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
                current_agent: Optional[str] = Field(default=None)
                tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
                final_answer: Optional[str] = Field(default=None)
            
            # Create the state graph
            graph = StateGraph(GraphState)
            
            # Track execution trace
            execution_trace = []
            
            # Create LLMs and tool configurations for each agent
            agent_nodes = {}
            for agent_config in flow.get("agents", []):
                # Create LLM
                llm = self._create_llm(agent_config)
                
                # Create tools
                tools = self._create_tools(agent_config.get("tools", []))
                
                # Define agent node function
                async def agent_node(state: GraphState) -> Dict[str, Any]:
                    # Prepare messages
                    messages = []
                    
                    # Add system message
                    system_msg = agent_config.get("system_message")
                    if system_msg:
                        messages.append(SystemMessage(content=system_msg))
                    
                    # Add conversation history
                    for msg in state.conversation_history:
                        if msg["role"] == "human":
                            messages.append(HumanMessage(content=msg["content"]))
                        elif msg["role"] == "agent":
                            messages.append(AIMessage(content=msg["content"]))
                        elif msg["role"] == "tool":
                            messages.append(FunctionMessage(
                                name=msg.get("name", "tool"), 
                                content=msg["content"]
                            ))
                    
                    # Add current query
                    messages.append(HumanMessage(content=state.query))
                    
                    # Call LLM
                    chain = llm.bind_tools(tools)
                    response = await chain.ainvoke(messages)
                    
                    # Update step trace
                    step_trace = {
                        "step": len(execution_trace) + 1,
                        "agent_id": agent_config.get("agent_id"),
                        "agent_name": agent_config.get("name"),
                        "input": {"query": state.query},
                        "output": {
                            "content": response.content if response.content else "",
                            "tool_calls": [
                                {"name": tool_call.name, "arguments": tool_call.args} 
                                for tool_call in response.tool_calls
                            ] if response.tool_calls else []
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    execution_trace.append(step_trace)
                    
                    # Call step callback if provided
                    if step_callback:
                        await step_callback(step_trace)
                    
                    # Prepare return state
                    new_state = {
                        "conversation_history": state.conversation_history + [
                            {"role": "agent", "content": response.content or ""}
                        ],
                        "tool_calls": [
                            {"tool": tool_call.name, "arguments": tool_call.args} 
                            for tool_call in response.tool_calls
                        ] if response.tool_calls else []
                    }
                    
                    # Check for tool execution
                    if response.tool_calls:
                        # Execute tools sequentially
                        for tool_call in response.tool_calls:
                            tool_name = tool_call.name
                            tool_args = tool_call.args
                            
                            # Execute tool
                            tool_result = await self.tool_registry.execute_tool(tool_name, tool_args)
                            
                            # Update trace
                            tool_trace = {
                                "step": len(execution_trace) + 1,
                                "type": "tool_execution",
                                "tool": tool_name,
                                "input": tool_args,
                                "output": tool_result,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                            execution_trace.append(tool_trace)
                            
                            # Call step callback if provided
                            if step_callback:
                                await step_callback(tool_trace)
                            
                            # Update conversation history with tool result
                            new_state["conversation_history"].append({
                                "role": "tool", 
                                "name": tool_name, 
                                "content": json.dumps(tool_result)
                            })
                    
                    return new_state
                
                # Store agent node for later use
                agent_nodes[agent_config.get("agent_id")] = agent_node
            
            # Add nodes to graph
            for agent_id, node_func in agent_nodes.items():
                graph.add_node(agent_id, node_func)
            
            # Add edges between agents (if not specified, create sequential flow)
            if len(agent_nodes) > 1:
                agent_ids = list(agent_nodes.keys())
                for i in range(len(agent_ids) - 1):
                    graph.add_edge(agent_ids[i], agent_ids[i+1])
            
            # Add a condition to route between nodes or end
            def router(state: GraphState):
                # If we want to stop, return END
                if state.final_answer:
                    return END
                
                # Continue to next agent or default behavior
                return state.current_agent or list(agent_nodes.keys())[0]
            
            graph.add_conditional_edges(
                list(agent_nodes.keys())[-1],  # Last agent
                router
            )
            
            # Set entry point
            graph.set_entry_point(list(agent_nodes.keys())[0])
            
            # Compile the graph
            compiled_graph = graph.compile(
                checkpointer=self.checkpoint_handler
            )
            
            # Prepare initial state
            initial_state = GraphState(
                query=input_data.get("query", ""),
                conversation_history=[],
                current_agent=None,
                tool_calls=[],
                final_answer=None
            )
            
            # Execute the graph
            final_state = {}
            async for state in compiled_graph.astream(initial_state):
                final_state = state
                
                # Optional: check for final answer condition
                if state.get("final_answer"):
                    break
            
            # Prepare final result
            result = {
                "output": {
                    "content": final_state.final_answer or final_state.conversation_history[-1]["content"],
                    "metadata": {
                        "framework": "langgraph",
                        "iterations": len(execution_trace)
                    }
                },
                "execution_trace": execution_trace,
                "steps": len(execution_trace)
            }
            
            return result
        
        except Exception as e:
            logger.exception(f"Error executing LangGraph flow: {str(e)}")
            return {
                "output": {
                    "error": str(e),
                    "metadata": {
                        "framework": "langgraph"
                    }
                },
                "execution_trace": [],
                "steps": 0
            }
