# backend/adapters/crewai/crewai_adapter.py
from typing import Dict, List, Any, Optional, Callable, Awaitable
import asyncio
import logging
import json
import importlib
import inspect
from datetime import datetime

from ...adapters.interfaces.base_adapter import FrameworkAdapter

logger = logging.getLogger(__name__)

class CrewAIAdapter(FrameworkAdapter):
    """Adapter for CrewAI framework"""
    
    def __init__(self):
        # Check if crewai is installed
        try:
            self.crewai_available = True
            import crewai
            self.crewai_version = crewai.__version__
            
            # Import CrewAI modules conditionally
            from crewai import Agent, Crew, Task
            self.Agent = Agent
            self.Crew = Crew
            self.Task = Task
            self.has_full_imports = True
        except ImportError:
            self.crewai_available = False
            logger.warning("CrewAI not installed - some functionality may be limited")
            self.has_full_imports = False
            
    def get_framework_name(self) -> str:
        return "crewai"
    
    def convert_flow(self, flow_config: Dict[str, Any]) -> Any:
        """Convert NexusFlow configuration to CrewAI format"""
        # Extract components from flow config
        agents = flow_config.get("agents", [])
        tools = flow_config.get("tools", {})
        max_steps = flow_config.get("max_steps", 10)
        
        # Create a proper CrewAI configuration
        # For MVP, we'll use a simplified representation that can be executed
        crewai_config = {
            "type": "crewai_flow",
            "agents": [],
            "tasks": [],
            "tools": {},
            "max_steps": max_steps,
            "original_config": flow_config
        }
        
        # Process agents
        for i, agent in enumerate(agents):
            agent_id = agent.get("agent_id", f"agent-{i}")
            agent_name = agent.get("name", f"Agent {i+1}")
            
            # Generate a role description if one is not provided
            role_description = agent.get("description", "")
            if not role_description:
                role_description = f"{agent_name} specialized in {', '.join(agent.get('capabilities', ['general tasks']))}"
            
            agent_config = {
                "id": agent_id,
                "name": agent_name,
                "role": role_description,
                "goal": f"Complete assigned tasks related to {agent_name}'s expertise",
                "backstory": agent.get("system_message", f"{agent_name} is an AI assistant specialized in {role_description}"),
                "model_provider": agent.get("model_provider", "openai"),
                "model_name": agent.get("model_name", "gpt-4"),
                "temperature": agent.get("temperature", 0.7),
                "tools": agent.get("tool_names", []),
                "allow_delegation": agent.get("can_delegate", True),
                "verbose": True
            }
            
            crewai_config["agents"].append(agent_config)
            
        # Create tasks based on agents (in CrewAI, each agent typically has a task)
        for i, agent_config in enumerate(crewai_config["agents"]):
            task_id = f"task-{i}"
            agent_id = agent_config["id"]
            
            # Generate a task description based on agent role
            task_description = f"Use your expertise as {agent_config['role']} to analyze and respond to the input query"
            
            task_config = {
                "id": task_id,
                "description": task_description,
                "agent_id": agent_id,
                "expected_output": "A comprehensive response based on your expertise",
                "tools": agent_config["tools"]
            }
            
            crewai_config["tasks"].append(task_config)
        
        # Process tools
        for tool_name, tool_config in tools.items():
            crewai_config["tools"][tool_name] = {
                "description": tool_config.get("description", ""),
                "config": tool_config.get("config", {}),
                "crewai_config": {
                    "allow_delegation": tool_config.get("config", {}).get("allow_delegation", True),
                    "timeout": tool_config.get("config", {}).get("timeout", 60)
                }
            }
            
        return crewai_config
    
    async def execute_flow(
        self, 
        flow: Any, 
        input_data: Dict[str, Any],
        step_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """
        Execute a CrewAI flow with the given input data
        
        Args:
            flow: CrewAI flow configuration
            input_data: Input data for the flow
            step_callback: Optional callback for streaming updates
            
        Returns:
            Dictionary containing execution results
        """
        if not self.crewai_available:
            raise RuntimeError("CrewAI is not installed or not properly configured")
        
        # In a production implementation, we would create a real CrewAI workflow
        # For MVP, we'll simulate the execution with proper tracing
        execution_trace = []
        
        # Extract components from the flow
        agents = flow.get("agents", [])
        tasks = flow.get("tasks", [])
        tools = flow.get("tools", {})
        max_steps = flow.get("max_steps", 10)
        
        if not agents:
            raise ValueError("No agents defined in the flow")
            
        # Initialize query
        query = input_data.get("query", "")
        if not query:
            raise ValueError("Input must contain a 'query' field")
            
        # Initialize state
        state = {
            "query": query,
            "conversation_history": [],
            "iteration": 0,
            "result": None
        }
        
        # Add any additional input data to the state
        for key, value in input_data.items():
            if key != "query":
                state[key] = value
                
        # Start with the first agent/task
        current_step = 1
        
        try:
            # In CrewAI, agents work on their assigned tasks in sequence or in parallel
            # For MVP, we'll simulate sequential execution
            for i, agent_config in enumerate(agents):
                agent_id = agent_config["id"]
                agent_name = agent_config["name"]
                
                # Find the task for this agent
                task = next((t for t in tasks if t["agent_id"] == agent_id), None)
                if not task:
                    # Create a default task if none is defined
                    task = {
                        "id": f"task-{i}",
                        "description": f"Process the query based on your expertise as {agent_name}",
                        "agent_id": agent_id,
                        "expected_output": "A comprehensive response"
                    }
                
                # Create step record for execution trace
                step_record = {
                    "step": current_step,
                    "agent_id": agent_id,
                    "agent_name": agent_name,
                    "type": "agent_execution",
                    "input": {
                        "query": state["query"],
                        "task": task["description"],
                        "conversation_history": state["conversation_history"]
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Simulate agent execution
                # In a real implementation, this would create a CrewAI Agent and execute the task
                agent_response = await self._simulate_agent_execution(
                    agent=agent_config,
                    task=task,
                    state=state,
                    tools=tools
                )
                
                # Update step record with agent response
                step_record["output"] = {
                    "content": agent_response.get("content", ""),
                    "metadata": {
                        "model": f"{agent_config['model_provider']}/{agent_config['model_name']}"
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
                    "name": agent_name,
                    "content": agent_response.get("content", "")
                })
                
                # Check if agent wants to use a tool
                if agent_response.get("use_tool"):
                    tool_name = agent_response.get("tool_name")
                    tool_input = agent_response.get("tool_input", {})
                    
                    # Check if tool exists and agent has access to it
                    agent_tools = agent_config.get("tools", [])
                    if tool_name in tools and tool_name in agent_tools:
                        # Create tool step record
                        tool_step = {
                            "step": current_step,
                            "agent_id": agent_id,
                            "agent_name": agent_name,
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
                        
                        # Process the tool results with the same agent
                        # This is how CrewAI typically works - agents use tools and then continue
                        tool_processing_step = {
                            "step": current_step,
                            "agent_id": agent_id,
                            "agent_name": agent_name,
                            "type": "agent_execution",
                            "input": {
                                "tool_result": tool_result,
                                "task": task["description"]
                            },
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        # Simulate agent processing tool results
                        process_response = await self._simulate_tool_processing(
                            agent=agent_config,
                            tool_name=tool_name,
                            tool_result=tool_result,
                            state=state
                        )
                        
                        # Update step with response
                        tool_processing_step["output"] = {
                            "content": process_response.get("content", ""),
                            "metadata": {
                                "model": f"{agent_config['model_provider']}/{agent_config['model_name']}"
                            }
                        }
                        
                        # Add to execution trace
                        execution_trace.append(tool_processing_step)
                        
                        # Notify callback if provided
                        if step_callback:
                            await step_callback(tool_processing_step)
                            
                        # Add to conversation history
                        state["conversation_history"].append({
                            "role": "agent",
                            "name": agent_name,
                            "content": process_response.get("content", "")
                        })
                        
                        # Update state if final answer is provided
                        if process_response.get("final_answer"):
                            if state.get("result"):
                                # Append to existing result
                                state["result"] += "\n\n" + process_response.get("final_answer")
                            else:
                                # Set as new result
                                state["result"] = process_response.get("final_answer")
                        
                        # Increment step counter
                        current_step += 1
                    
                # Check if agent wants to delegate to another agent
                elif agent_response.get("delegate_to"):
                    delegate_to = agent_response.get("delegate_to")
                    delegate_task = agent_response.get("delegate_task", "")
                    delegation_reason = agent_response.get("delegation_reason", "")
                    
                    # Find target agent
                    target_agent = next((a for a in agents if a["id"] == delegate_to), None)
                    
                    if target_agent and agent_config.get("allow_delegation", True):
                        # Create delegation step
                        delegation_step = {
                            "step": current_step,
                            "agent_id": agent_id,
                            "agent_name": agent_name,
                            "type": "delegation",
                            "decision": {
                                "action": "delegate",
                                "target": delegate_to,
                                "target_name": target_agent.get("name", "Unknown agent"),
                                "task": delegate_task,
                                "reasoning": delegation_reason
                            },
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        # Add to execution trace
                        execution_trace.append(delegation_step)
                        
                        # Notify callback if provided
                        if step_callback:
                            await step_callback(delegation_step)
                            
                        # Add to conversation history
                        state["conversation_history"].append({
                            "role": "system",
                            "content": f"Delegating to {target_agent.get('name')}: {delegation_reason}"
                        })
                        
                        # Increment step counter
                        current_step += 1
                        
                        # Execute the delegated task
                        delegation_execution_step = {
                            "step": current_step,
                            "agent_id": delegate_to,
                            "agent_name": target_agent.get("name", "Unknown agent"),
                            "type": "agent_execution",
                            "input": {
                                "query": state["query"],
                                "task": delegate_task,
                                "delegation_from": agent_name,
                                "conversation_history": state["conversation_history"]
                            },
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        # Simulate delegated agent execution
                        delegated_response = await self._simulate_agent_execution(
                            agent=target_agent,
                            task={"description": delegate_task},
                            state=state,
                            tools=tools
                        )
                        
                        # Update step with response
                        delegation_execution_step["output"] = {
                            "content": delegated_response.get("content", ""),
                            "metadata": {
                                "model": f"{target_agent['model_provider']}/{target_agent['model_name']}"
                            }
                        }
                        
                        # Add to execution trace
                        execution_trace.append(delegation_execution_step)
                        
                        # Notify callback if provided
                        if step_callback:
                            await step_callback(delegation_execution_step)
                            
                        # Add to conversation history
                        state["conversation_history"].append({
                            "role": "agent",
                            "name": target_agent.get("name", "Unknown agent"),
                            "content": delegated_response.get("content", "")
                        })
                        
                        # Update state if final answer is provided
                        if delegated_response.get("final_answer"):
                            if state.get("result"):
                                # Append to existing result
                                state["result"] += "\n\n" + delegated_response.get("final_answer")
                            else:
                                # Set as new result
                                state["result"] = delegated_response.get("final_answer")
                                
                        # Increment step counter
                        current_step += 1
                        
                # Check if agent has final answer
                elif agent_response.get("final_answer"):
                    if state.get("result"):
                        # Append to existing result
                        state["result"] += "\n\n" + agent_response.get("final_answer")
                    else:
                        # Set as new result
                        state["result"] = agent_response.get("final_answer")
                
                # Increment iteration counter
                state["iteration"] += 1
            
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
                
            # If no result was set, use the last agent response
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
                        "framework": "crewai",
                        "agents": len(agents),
                        "steps": current_step - 1
                    }
                },
                "execution_trace": execution_trace,
                "steps": len(execution_trace)
            }
            
            return result
            
        except Exception as e:
            logger.exception(f"Error executing CrewAI flow: {str(e)}")
            
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
                        "framework": "crewai",
                        "iterations": state["iteration"]
                    }
                },
                "execution_trace": execution_trace,
                "steps": len(execution_trace)
            }
    
    async def _simulate_agent_execution(
        self, 
        agent: Dict[str, Any], 
        task: Dict[str, Any],
        state: Dict[str, Any],
        tools: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate CrewAI agent execution for the MVP
        In a real implementation, this would create a CrewAI Agent and execute the task
        
        Args:
            agent: Agent configuration
            task: Task configuration
            state: Current state
            tools: Available tools
            
        Returns:
            Simulated agent response
        """
        # For the MVP, we'll return a simulated response
        # In production, this would use CrewAI to create and run the agent
        
        # Simplified logic for the simulation (can be expanded later)
        query = state.get("query", "")
        iteration = state.get("iteration", 0)
        agent_name = agent.get("name", "Agent")
        agent_role = agent.get("role", "")
        agent_tools = agent.get("tools", [])
        task_description = task.get("description", "")
        
        # Simulate some processing time
        await asyncio.sleep(0.5)
        
        # Basic simulation logic based on agent role and task
        if "researcher" in agent_role.lower() or "research" in task_description.lower():
            # Research-oriented agent behavior
            if "web_search" in agent_tools:
                return {
                    "content": f"As a {agent_role}, I'll search for information about '{query}'",
                    "use_tool": True,
                    "tool_name": "web_search",
                    "tool_input": {"query": query, "num_results": 3}
                }
            else:
                # Find an agent who can do search
                search_capable_agents = [
                    a for a in state.get("_all_agents", []) 
                    if "web_search" in a.get("tools", [])
                ]
                
                if search_capable_agents:
                    delegate_to = search_capable_agents[0]["id"]
                    return {
                        "content": f"I need to research '{query}' but don't have search capabilities. I'll delegate to another agent.",
                        "delegate_to": delegate_to,
                        "delegate_task": f"Please research information about '{query}'",
                        "delegation_reason": "Need search capabilities"
                    }
                else:
                    return {
                        "content": f"Based on my expertise as {agent_role}, I'll analyze '{query}' with the information available.",
                        "final_answer": f"As a {agent_role}, my analysis of '{query}' reveals: [simulated research-based answer without external data]"
                    }
        
        elif "analyst" in agent_role.lower() or "analysis" in task_description.lower():
            # Analysis-oriented agent behavior
            tool_result = state.get("tool_result")
            if tool_result and "data_analysis" in agent_tools:
                return {
                    "content": f"As {agent_role}, I'll analyze the data about '{query}'",
                    "use_tool": True,
                    "tool_name": "data_analysis",
                    "tool_input": {"data": tool_result, "analysis_type": "exploratory"}
                }
            else:
                return {
                    "content": f"I've analyzed the information about '{query}' based on my expertise as {agent_role}.",
                    "final_answer": f"My analysis as {agent_role} shows: [simulated analytical response about {query}]"
                }
        
        elif "writer" in agent_role.lower() or "write" in task_description.lower():
            # Writing-oriented agent behavior
            return {
                "content": f"As {agent_role}, I'll write content related to '{query}'",
                "final_answer": f"[Simulated written content about {query} as {agent_role}]"
            }
            
        elif "coder" in agent_role.lower() or "code" in task_description.lower():
            # Coding-oriented agent behavior
            if "code_execution" in agent_tools:
                return {
                    "content": f"As {agent_role}, I'll write code to address '{query}'",
                    "use_tool": True,
                    "tool_name": "code_execution",
                    "tool_input": {
                        "language": "python",
                        "code": f"# Code to address: {query}\nprint('This is simulated code for {query}')\nresult = 'Simulated result'\nprint(f'Result: {result}')"
                    }
                }
            else:
                return {
                    "content": f"As {agent_role}, I've written code to address '{query}'",
                    "final_answer": f"Here's the code to address '{query}':\n```python\n# Simulated code\ndef solve_problem():\n    return 'Solution'\n```"
                }
        
        else:
            # Generic agent behavior
            if agent_tools and iteration == 0:
                # First iteration and has tools - use one
                tool_name = agent_tools[0]
                return {
                    "content": f"As {agent_role}, I'll use {tool_name} to help with '{query}'",
                    "use_tool": True,
                    "tool_name": tool_name,
                    "tool_input": {"query": query}
                }
            else:
                # Generic response
                return {
                    "content": f"I've completed my task as {agent_role} regarding '{query}'",
                    "final_answer": f"Based on my expertise as {agent_role}, here's my response to '{query}': [simulated response based on {agent_role}]"
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
        
        # Simplified simulation based on tool name (same as in LangGraph adapter)
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
        Register tools with CrewAI
        
        Args:
            tools: List of tool configurations
            framework_config: Optional CrewAI-specific configuration
            
        Returns:
            CrewAI-specific tool configuration
        """
        if not self.crewai_available:
            raise RuntimeError("CrewAI is not installed or not properly configured")
            
        # For MVP, we'll create a simplified tool registry
        # In a real implementation, this would register tools with CrewAI
        
        registered_tools = {}
        
        for tool in tools:
            tool_name = tool.get("name")
            if not tool_name:
                continue
                
            # Extract CrewAI specific configuration
            crewai_config = tool.get("config", {})
            allow_delegation = crewai_config.get("allow_delegation", True)
            timeout = crewai_config.get("timeout", 60)
            
            # Create CrewAI tool configuration
            registered_tools[tool_name] = {
                "description": tool.get("description", ""),
                "parameters": tool.get("parameters", {}),
                "crewai_config": {
                    "allow_delegation": allow_delegation,
                    "timeout": timeout
                },
                "function_name": tool.get("function_name")
            }
        
        return {
            "registered_tools": registered_tools,
            "framework": "crewai"
        }
        
    def get_supported_features(self) -> Dict[str, bool]:
        """Return features supported by CrewAI"""
        return {
            "multi_agent": True,
            "parallel_execution": False,
            "tools": True,
            "streaming": False,
            "visualization": True
        }
        
    def validate_flow(self, flow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a flow configuration for CrewAI
        
        Args:
            flow_config: Flow configuration to validate
            
        Returns:
            Dictionary with validation results
        """
        # Start with basic validation from parent class
        validation_result = super().validate_flow(flow_config)
        
        # Additional CrewAI-specific validations
        agents = flow_config.get("agents", [])
        
        # Check for valid model providers
        for i, agent in enumerate(agents):
            provider = agent.get("model_provider", "")
            if provider and provider not in ["openai", "anthropic"]:
                validation_result["warnings"].append(
                    f"Agent {i+1}: Model provider '{provider}' may not be fully compatible with CrewAI"
                )
                
            # Check for system message (CrewAI uses backstory instead)
            if agent.get("system_message") and not agent.get("description"):
                validation_result["warnings"].append(
                    f"Agent {i+1}: CrewAI works best with a role description in addition to system message"
                )
                
        return validation_result
        
    def get_default_agent_config(self) -> Dict[str, Any]:
        """Get default configuration for a CrewAI agent"""
        return {
            "name": "Default CrewAI Agent",
            "description": "Default role for CrewAI agents",
            "model_provider": "openai",
            "model_name": "gpt-4",
            "temperature": 0.7,
            "system_message": "You are a helpful AI assistant working within a CrewAI team.",
            "capabilities": ["reasoning"],
            "tool_names": [],
            "can_delegate": True  # CrewAI specific
        }
        
    async def visualize_flow(
        self, 
        flow: Any, 
        format: str = "json",
        include_tools: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a CrewAI-specific visualization of the flow
        
        Args:
            flow: CrewAI flow object
            format: Desired format ('json', 'mermaid', 'dot')
            include_tools: Whether to include tool nodes
            
        Returns:
            Dictionary containing visualization data
        """
        # Extract components from the flow
        agents = flow.get("agents", [])
        tasks = flow.get("tasks", [])
        tools = flow.get("tools", {})
        
        # Prepare nodes and connections
        nodes = []
        connections = []
        
        # Add agent nodes
        for agent in agents:
            nodes.append({
                "id": agent["id"],
                "name": agent["name"],
                "role": agent.get("role", ""),
                "type": "agent",
                "agent_type": "crewai",
                "model": f"{agent['model_provider']}/{agent['model_name']}",
                "allow_delegation": agent.get("allow_delegation", True),
                "tools": agent.get("tools", [])
            })
            
        # Add a crew manager node in the center
        nodes.append({
            "id": "crew-manager",
            "name": "Crew Manager",
            "type": "manager",
            "description": "Coordinates the CrewAI team"
        })
        
        # Connect crew manager to all agents
        for agent in agents:
            connections.append({
                "source": "crew-manager",
                "target": agent["id"],
                "type": "management"
            })
            
        # Connect agents to their tasks
        for task in tasks:
            agent_id = task.get("agent_id")
            if agent_id:
                task_id = f"task-{task.get('id', agent_id)}"
                
                # Add task node
                nodes.append({
                    "id": task_id,
                    "name": task.get("description", "Task"),
                    "type": "task",
                    "expected_output": task.get("expected_output", "")
                })
                
                # Connect agent to task
                connections.append({
                    "source": agent_id,
                    "target": task_id,
                    "type": "executes"
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
                
                # Connect tools to agents that use them
                for agent in agents:
                    if tool_name in agent.get("tools", []):
                        connections.append({
                            "source": agent["id"],
                            "target": tool_id,
                            "type": "uses"
                        })
        
        # Format output based on requested format
        if format == "mermaid":
            mermaid_output = self._generate_mermaid(nodes, connections)
            return {
                "nodes": nodes,
                "edges": connections,
                "framework": "crewai",
                "format": "mermaid",
                "mermaid": mermaid_output
            }
        elif format == "dot":
            dot_output = self._generate_dot(nodes, connections)
            return {
                "nodes": nodes,
                "edges": connections,
                "framework": "crewai",
                "format": "dot",
                "dot": dot_output
            }
        else:
            # Default JSON format
            return {
                "nodes": nodes,
                "edges": connections,
                "framework": "crewai",
                "format": "json"
            }
            
    def _generate_mermaid(self, nodes: List[Dict[str, Any]], connections: List[Dict[str, Any]]) -> str:
        """Generate Mermaid diagram for the flow"""
        mermaid = ["graph TD;"]
        
        # Add nodes
        for node in nodes:
            node_id = node["id"]
            node_name = node.get("name", "")
            node_type = node.get("type", "")
            node_desc = ""
            
            if node.get("role"):
                node_desc = f" ({node['role']})"
                
            # Style based on node type
            if node_type == "agent":
                mermaid.append(f'  {node_id}["{node_name}{node_desc}"] class agentStyle;')
            elif node_type == "manager":
                mermaid.append(f'  {node_id}(("{node_name}")) class managerStyle;')
            elif node_type == "task":
                mermaid.append(f'  {node_id}["{node_name}"] class taskStyle;')
            elif node_type == "tool":
                mermaid.append(f'  {node_id}["{node_name}"] class toolStyle;')
            else:
                mermaid.append(f'  {node_id}["{node_name}"];')
                
        # Add connections
        for conn in connections:
            source = conn["source"]
            target = conn["target"]
            label = conn.get("type", "")
            
            if label:
                mermaid.append(f'  {source} -->|"{label}"| {target};')
            else:
                mermaid.append(f'  {source} --> {target};')
                
        # Add styles
        mermaid.append("  classDef agentStyle fill:#E8DAEF,stroke:#8E44AD,color:#000;")
        mermaid.append("  classDef managerStyle fill:#D5F5E3,stroke:#2ECC71,color:#000;")
        mermaid.append("  classDef taskStyle fill:#D6EAF8,stroke:#3498DB,color:#000;")
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
            node_name = node.get("name", "")
            node_type = node.get("type", "")
            
            node_label = node_name
            if node.get("role"):
                node_label += f"\\n({node['role']})"
                
            # Style based on node type
            if node_type == "agent":
                dot.append(f'  "{node_id}" [label="{node_label}", fillcolor="#E8DAEF", style="filled,rounded", color="#8E44AD"];')
            elif node_type == "manager":
                dot.append(f'  "{node_id}" [label="{node_label}", shape=ellipse, fillcolor="#D5F5E3", style="filled", color="#2ECC71"];')
            elif node_type == "task":
                dot.append(f'  "{node_id}" [label="{node_label}", fillcolor="#D6EAF8", style="filled,rounded", color="#3498DB"];')
            elif node_type == "tool":
                dot.append(f'  "{node_id}" [label="{node_label}", fillcolor="#FCF3CF", style="filled,rounded", color="#F1C40F"];')
            else:
                dot.append(f'  "{node_id}" [label="{node_label}"];')
                
        # Add connections
        for conn in connections:
            source = conn["source"]
            target = conn["target"]
            label = conn.get("type", "")
            
            if label:
                dot.append(f'  "{source}" -> "{target}" [label="{label}"];')
            else:
                dot.append(f'  "{source}" -> "{target}";')
                
        dot.append("}")
        
        return "\n".join(dot)
