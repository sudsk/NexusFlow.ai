# backend/api/models/flow_models.py
from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

# Base Flow model
class FlowBase(BaseModel):
    """Base model for flow data"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    framework: str = Field("langgraph", min_length=1)
    max_steps: int = Field(10, ge=1, le=100)
    
    @validator('framework')
    def validate_framework(cls, v):
        """Validate the framework is supported"""
        allowed_frameworks = ["langgraph", "crewai", "autogen", "dspy"]
        if v not in allowed_frameworks:
            raise ValueError(f"Framework must be one of: {', '.join(allowed_frameworks)}")
        return v

# Agent model
class AgentCreate(BaseModel):
    """Agent configuration"""
    name: str = Field(..., min_length=1, max_length=100)
    agent_id: Optional[str] = None
    model_provider: str = Field(..., min_length=1)
    model_name: str = Field(..., min_length=1)
    system_message: Optional[str] = None
    temperature: float = Field(0.7, ge=0, le=1)
    capabilities: List[str] = Field(default_factory=list)
    tool_names: List[str] = Field(default_factory=list)
    can_delegate: Optional[bool] = True

# Tool configuration
class ToolConfig(BaseModel):
    """Tool configuration for a flow"""
    description: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)

# Flow creation request
class FlowCreateRequest(FlowBase):
    """Request model for creating a flow"""
    agents: List[AgentCreate] = Field(..., min_items=1)
    tools: Dict[str, ToolConfig] = Field(default_factory=dict)

# Flow update request
class FlowUpdateRequest(BaseModel):
    """Request model for updating a flow"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    framework: Optional[str] = None
    max_steps: Optional[int] = Field(None, ge=1, le=100)
    agents: Optional[List[AgentCreate]] = None
    tools: Optional[Dict[str, ToolConfig]] = None
    
    @validator('framework')
    def validate_framework(cls, v):
        """Validate the framework is supported"""
        if v is None:
            return v
        allowed_frameworks = ["langgraph", "crewai", "autogen", "dspy"]
        if v not in allowed_frameworks:
            raise ValueError(f"Framework must be one of: {', '.join(allowed_frameworks)}")
        return v

# Flow response model
class FlowResponse(FlowBase):
    """Response model for flow data"""
    flow_id: str
    agents: List[AgentCreate]
    tools: Dict[str, ToolConfig] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Flow list response
class FlowListResponse(BaseModel):
    """Response model for listing flows"""
    items: List[FlowResponse]
    total: int
    page: int = 1
    page_size: int = 100

# Flow execution request
class FlowExecutionRequest(BaseModel):
    """Request model for executing a flow"""
    input: Dict[str, Any] = Field(..., description="Input data for the flow")
    framework: Optional[str] = Field(None, description="Framework to use for execution")

# Flow execution response
class FlowExecutionResponse(BaseModel):
    """Response model for flow execution results"""
    execution_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Flow validation response
class FlowValidationResponse(BaseModel):
    """Response model for flow validation"""
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

# Flow export response
class FlowExportResponse(BaseModel):
    """Response model for flow export"""
    flow_id: str
    original_framework: str
    target_framework: str
    exported_config: Dict[str, Any]
