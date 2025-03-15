"""
Node system for NexusFlow.ai

This module defines the Node class that represents a unit of computation in a flow.
Nodes can represent agents, tools, or other processing elements in the workflow.
"""

from typing import Dict, List, Any, Optional, Union, Callable, Awaitable
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class Node:
    """
    Base node class for workflow graph representation
    
    A node represents any entity in the workflow that can process inputs and produce outputs,
    such as an agent, a tool, or a decision point.
    """
    
    def __init__(
        self,
        node_id: Optional[str] = None,
        node_type: str = "generic",
        name: Optional[str] = None,
        description: Optional[str] = None,
        handler: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a node
        
        Args:
            node_id: Unique ID for the node (generated if not provided)
            node_type: Type of the node (agent, tool, router, etc.)
            name: Human-readable name of the node
            description: Description of the node
            handler: Function to call when executing the node
            metadata: Additional metadata for the node
        """
        self.node_id = node_id or str(uuid.uuid4())
        self.node_type = node_type
        self.name = name or f"{node_type.capitalize()} Node"
        self.description = description or f"A {node_type} node"
        self.handler = handler
        self.metadata = metadata or {}
        
        # Node state
        self.inputs = []
        self.outputs = []
        self.errors = []
        self.created_at = datetime.utcnow().isoformat()
        self.last_executed = None
        self.execution_count = 0
    
    async def process(self, input_data: Any, context: Dict[str, Any] = None) -> Any:
        """
        Process input data through this node
        
        Args:
            input_data: Input data to process
            context: Additional context for processing
            
        Returns:
            Processing result
        """
        context = context or {}
        
        # Record input
        self.inputs.append({
            "data": input_data,
            "timestamp": datetime.utcnow().isoformat(),
            "context_keys": list(context.keys())
        })
        
        # Execute handler if provided
        result = None
        try:
            self.last_executed = datetime.utcnow().isoformat()
            self.execution_count += 1
            
            if self.handler:
                if isinstance(self.handler, Awaitable) or hasattr(self.handler, '__await__'):
                    result = await self.handler(input_data, context)
                else:
                    result = self.handler(input_data, context)
            else:
                # Default passthrough behavior
                result = input_data
            
            # Record output
            self.outputs.append({
                "data": result,
                "timestamp": datetime.utcnow().isoformat(),
                "execution_id": self.execution_count
            })
            
            return result
            
        except Exception as e:
            error_info = {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "input": input_data,
                "execution_id": self.execution_count
            }
            self.errors.append(error_info)
            logger.error(f"Error in node {self.node_id} ({self.name}): {str(e)}")
            raise
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "last_executed": self.last_executed,
            "execution_count": self.execution_count,
            "inputs_count": len(self.inputs),
            "outputs_count": len(self.outputs),
            "errors_count": len(self.errors)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Node':
        """Create node from dictionary"""
        node = cls(
            node_id=data.get("node_id"),
            node_type=data.get("node_type", "generic"),
            name=data.get("name"),
            description=data.get("description"),
            metadata=data.get("metadata", {})
        )
        
        node.created_at = data.get("created_at", datetime.utcnow().isoformat())
        node.last_executed = data.get("last_executed")
        node.execution_count = data.get("execution_count", 0)
        
        return node


class AgentNode(Node):
    """Node that represents an agent in the workflow"""
    
    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        capabilities: List[str] = None,
        model_info: Dict[str, str] = None,
        can_delegate: bool = True,
        **kwargs
    ):
        """
        Initialize an agent node
        
        Args:
            agent_id: ID of the agent
            agent_name: Name of the agent
            capabilities: List of capability IDs
            model_info: Information about the model used by the agent
            can_delegate: Whether the agent can delegate to other agents
            **kwargs: Additional parameters to pass to Node constructor
        """
        super().__init__(
            node_id=agent_id,
            node_type="agent",
            name=agent_name,
            **kwargs
        )
        
        self.capabilities = capabilities or []
        self.model_info = model_info or {}
        self.can_delegate = can_delegate
        
        # Additional state for agent nodes
        self.decisions = []
    
    def add_decision(self, decision: Dict[str, Any]) -> None:
        """
        Add a decision made by this agent
        
        Args:
            decision: Decision information
        """
        self.decisions.append({
            **decision,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent node to dictionary representation"""
        node_dict = super().to_dict()
        return {
            **node_dict,
            "capabilities": self.capabilities,
            "model_info": self.model_info,
            "can_delegate": self.can_delegate,
            "decisions_count": len(self.decisions)
        }


class ToolNode(Node):
    """Node that represents a tool in the workflow"""
    
    def __init__(
        self,
        tool_id: str,
        tool_name: str,
        parameters: Dict[str, Any] = None,
        requires_auth: bool = False,
        **kwargs
    ):
        """
        Initialize a tool node
        
        Args:
            tool_id: ID of the tool
            tool_name: Name of the tool
            parameters: Parameter schema for the tool
            requires_auth: Whether the tool requires authentication
            **kwargs: Additional parameters to pass to Node constructor
        """
        super().__init__(
            node_id=tool_id,
            node_type="tool",
            name=tool_name,
            **kwargs
        )
        
        self.parameters = parameters or {}
        self.requires_auth = requires_auth
        
        # Additional state for tool nodes
        self.executions = []
    
    def add_execution(self, params: Dict[str, Any], result: Any) -> None:
        """
        Add an execution record for this tool
        
        Args:
            params: Parameters used for the execution
            result: Result of the execution
        """
        self.executions.append({
            "params": params,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool node to dictionary representation"""
        node_dict = super().to_dict()
        return {
            **node_dict,
            "parameters": self.parameters,
            "requires_auth": self.requires_auth,
            "executions_count": len(self.executions)
        }


class RouterNode(Node):
    """Node that routes execution based on conditions"""
    
    def __init__(
        self,
        router_id: Optional[str] = None,
        name: str = "Router",
        routes: Dict[str, Callable] = None,
        default_route: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize a router node
        
        Args:
            router_id: ID of the router
            name: Name of the router
            routes: Dictionary mapping route names to condition functions
            default_route: Default route if no conditions match
            **kwargs: Additional parameters to pass to Node constructor
        """
        super().__init__(
            node_id=router_id,
            node_type="router",
            name=name,
            **kwargs
        )
        
        self.routes = routes or {}
        self.default_route = default_route
        
        # Additional state for router nodes
        self.routing_history = []
    
    async def route(self, input_data: Any, context: Dict[str, Any] = None) -> str:
        """
        Determine the next route based on input data and context
        
        Args:
            input_data: Input data to route
            context: Additional context for routing
            
        Returns:
            Name of the selected route
        """
        context = context or {}
        
        # Evaluate routes in order
        for route_name, condition in self.routes.items():
            try:
                if await condition(input_data, context):
                    # Record routing decision
                    self.routing_history.append({
                        "input": input_data,
                        "selected_route": route_name,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    return route_name
            except Exception as e:
                logger.error(f"Error evaluating route condition '{route_name}': {str(e)}")
        
        # Use default route if available
        if self.default_route:
            self.routing_history.append({
                "input": input_data,
                "selected_route": self.default_route,
                "reason": "default",
                "timestamp": datetime.utcnow().isoformat()
            })
            return self.default_route
        
        # No route found
        self.routing_history.append({
            "input": input_data,
            "selected_route": None,
            "reason": "no_match",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        raise ValueError("No matching route found and no default route specified")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert router node to dictionary representation"""
        node_dict = super().to_dict()
        return {
            **node_dict,
            "routes": list(self.routes.keys()),
            "default_route": self.default_route,
            "routing_history_count": len(self.routing_history)
        }
