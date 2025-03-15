"""
API components for NexusFlow.ai

This package contains API components for the NexusFlow system:
- Routes: FastAPI route definitions
- Models: Pydantic models for API requests and responses
- Server: FastAPI server configuration
"""

from fastapi import APIRouter

# Create a router that can be included in a FastAPI app
router = APIRouter(prefix="/api/nexusflow", tags=["nexusflow"])

# Import models for easier access
from nexusflow.api.models import (
    ExecuteRequest,
    ExecuteResponse,
    CapabilityDefinition,
    FlowCreateRequest,
    FlowResponse,
    DeployRequest,
    DeployResponse,
    FlowExecutionRequest,
    FlowExecutionResponse,
    SearchFlowsRequest,
    WebhookConfig
)

# Import routes to register them with the router
from nexusflow.api.routes import (
    execute_flow,
    get_capabilities,
    analyze_input,
    create_flow,
    list_flows,
    get_flow,
    update_flow,
    delete_flow,
    execute_flow_by_id,
    get_execution,
    deploy_flow,
    create_webhook,
    execute_deployed_flow
)

__all__ = [
    # Router
    'router',
    
    # Models
    'ExecuteRequest',
    'ExecuteResponse',
    'CapabilityDefinition',
    'FlowCreateRequest',
    'FlowResponse',
    'DeployRequest',
    'DeployResponse',
    'FlowExecutionRequest',
    'FlowExecutionResponse',
    'SearchFlowsRequest',
    'WebhookConfig',
]
