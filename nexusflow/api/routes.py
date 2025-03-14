"""
API routes for NexusFlow.ai

This module defines the FastAPI routes for the NexusFlow API.
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from nexusflow.core.agent import Agent
from nexusflow.core.flow import Flow
from nexusflow.core.capability import capability_registry, CapabilityType

logger = logging.getLogger(__name__)

# Pydantic models for API
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

class FlowConfig(BaseModel):
    """Configuration for a flow"""
    name: str
    description: Optional[str] = None
    agents: List[AgentConfig] = []
    max_steps: int = 10
    tools: Dict[str, Any] = {}

class ExecuteRequest(BaseModel):
    """Request to execute a flow"""
    flow_config: FlowConfig
    input: Dict[str, Any]

class ExecuteResponse(BaseModel):
    """Response from executing a flow"""
    flow_id: str
    output: Dict[str, Any]
    steps: int
    execution_trace: List[Dict[str, Any]]
    timestamp: str

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

router = APIRouter()

@router.post("/execute", response_model=ExecuteResponse)
async def execute_flow(request: ExecuteRequest):
    """
    Execute a flow with the given configuration and input
    
    Args:
        request: Request to execute a flow
        
    Returns:
        Results of the flow execution
    """
    try:
        # Create agents from the configuration
        agents = []
        for agent_config in request.flow_config.agents:
            agent = Agent(
                name=agent_config.name,
                description=agent_config.description,
                capabilities=agent_config.capabilities,
                model_provider=agent_config.model_provider,
                model_name=agent_config.model_name,
                system_message=agent_config.system_message,
                temperature=agent_config.temperature,
                max_tokens=agent_config.max_tokens,
                tool_names=agent_config.tool_names,
                can_delegate=agent_config.can_delegate
            )
            agents.append(agent)
        
        # Create flow from the configuration
        flow = Flow(
            name=request.flow_config.name,
            description=request.flow_config.description,
            agents=agents,
            max_steps=request.flow_config.max_steps,
            tools=request.flow_config.tools
        )
        
        # Execute flow
        result = await flow.execute(request.input)
        
        # Return result
        return ExecuteResponse(
            flow_id=flow.flow_id,
            output=result.get("output", {}).to_dict() if hasattr(result.get("output", {}), "to_dict") else result.get("output", {}),
            steps=result.get("steps", 0),
            execution_trace=result.get("execution_trace", []),
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.exception(f"Error executing flow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/capabilities", response_model=List[CapabilityDefinition])
async def get_capabilities():
    """
    Get all available capabilities
    
    Returns:
        List of capability definitions
    """
    try:
        # Get all capability definitions from the registry
        capabilities = []
        for capability_type in CapabilityType.all():
            definition = capability_registry.get_capability_definition(capability_type)
            if definition:
                capabilities.append(CapabilityDefinition(
                    type=definition.type,
                    name=definition.name,
                    description=definition.description,
                    parameters=definition.parameters,
                    requires_tools=definition.requires_tools,
                    provides_output=definition.provides_output,
                    requires_input=definition.requires_input,
                    examples=definition.examples
                ))
        
        return capabilities
    
    except Exception as e:
        logger.exception(f"Error getting capabilities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-input", response_model=List[str])
async def analyze_input(input_data: Dict[str, Any]):
    """
    Analyze input to determine required capabilities
    
    Args:
        input_data: Input data to analyze
        
    Returns:
        List of required capability types
    """
    try:
        # Analyze input to determine required capabilities
        required_capabilities = capability_registry.analyze_required_capabilities(input_data)
        
        return required_capabilities
    
    except Exception as e:
        logger.exception(f"Error analyzing input: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
