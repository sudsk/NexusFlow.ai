"""
API data models for NexusFlow.ai

This module defines the Pydantic models used for API requests and responses.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class AgentConfig(BaseModel):
    """Configuration for an agent"""
    name: str
    description: Optional[str] = None
    capabilities: List[str] = []
    model_provider: str = "openai"
    model_name: str = "gpt-4"
    system_message: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    tool_names: List[str] = []
    can_delegate: bool = True
    
    model_config = ConfigDict(
        extra='allow'  # Allow extra fields for future extension
    )

class ToolDefinition(BaseModel):
    """Definition of a tool"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function_name: Optional[str] = None
    
    model_config = ConfigDict(
        extra='allow'
    )

class FlowConfig(BaseModel):
    """Configuration for a flow"""
    name: str
    description: Optional[str] = None
    agents: List[AgentConfig] = []
    max_steps: int = 10
    tools: Dict[str, Dict[str, Any]] = {}
    
    model_config = ConfigDict(
        extra='allow'
    )

class ExecuteRequest(BaseModel):
    """Request to execute a flow"""
    flow_config: FlowConfig
    input: Dict[str, Any]
    
    model_config = ConfigDict(
        extra='allow'
    )

class ExecuteResponse(BaseModel):
    """Response from executing a flow"""
    flow_id: str
    output: Dict[str, Any]
    steps: int
    execution_trace: List[Dict[str, Any]]
    timestamp: str
    
    model_config = ConfigDict(
        extra='allow'
    )

class CapabilityDefinition(BaseModel):
    """Definition of a capability"""
    type: str
    name: str
    description: str
    parameters: Dict[str, Any] = {}
    requires_tools: List[str] = []
    provides_output: List[str] = []
    requires_input: List[str] = []
    examples: List[Dict[str, Any]] = []
    
    model_config = ConfigDict(
        extra='allow'
    )

class FlowCreateRequest(BaseModel):
    """Request to create a new flow"""
    flow_config: FlowConfig
    
    model_config = ConfigDict(
        extra='allow'
    )

class FlowResponse(BaseModel):
    """Response containing flow details"""
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    config: FlowConfig
    
    model_config = ConfigDict(
        extra='allow'
    )

class DeployRequest(BaseModel):
    """Request to deploy a flow"""
    flow_id: str
    version: str = "v1"
    description: Optional[str] = None
    
    model_config = ConfigDict(
        extra='allow'
    )

class DeployResponse(BaseModel):
    """Response from deploying a flow"""
    deployment_id: str
    api_key: str
    endpoint_url: str
    status: str
    deployed_at: str
    
    model_config = ConfigDict(
        extra='allow'
    )

class FlowExecutionRequest(BaseModel):
    """Request to execute a deployed flow"""
    input: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        extra='allow'
    )

class FlowExecutionResponse(BaseModel):
    """Response from executing a deployed flow"""
    execution_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    model_config = ConfigDict(
        extra='allow'
    )

class SearchFlowsRequest(BaseModel):
    """Request to search for flows"""
    query: Optional[str] = None
    tags: List[str] = []
    limit: int = 10
    offset: int = 0
    
    model_config = ConfigDict(
        extra='allow'
    )

class WebhookConfig(BaseModel):
    """Configuration for a webhook"""
    url: str
    events: List[str] = ["completed", "failed"]
    secret: Optional[str] = None
    
    model_config = ConfigDict(
        extra='allow'
    )

class AgentDecisionModel(BaseModel):
    """Model representing an agent's decision"""
    agent_name: str
    action_type: str
    target: Optional[str] = None
    content: Optional[str] = None
    reasoning: Optional[str] = None
    tool_name: Optional[str] = None
    tool_params: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        extra='allow'
    )

class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    status_code: int
    type: Optional[str] = None
    
    model_config = ConfigDict(
        extra='allow'
    )
