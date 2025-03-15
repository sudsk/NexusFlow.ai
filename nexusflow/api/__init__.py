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

# Import routes to register them with the router
from nexusflow.api.routes import (
    execute_flow,
    get_capabilities,
    analyze_input
)

# Import models for easier access
# from nexusflow.api.models import (
#     ExecuteRequest,
#     ExecuteResponse,
#     CapabilityDefinition
# )

__all__ = [
    # Router
    'router',
]
