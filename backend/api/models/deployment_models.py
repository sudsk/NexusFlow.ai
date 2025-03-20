# backend/api/models/deployment_models.py
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

class DeploymentCreateRequest(BaseModel):
    """Request model for creating a deployment"""
    name: Optional[str] = None
    version: str = "v1"
    settings: Optional[Dict[str, Any]] = None

class DeploymentUpdateRequest(BaseModel):
    """Request model for updating a deployment"""
    name: Optional[str] = None
    status: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class DeploymentResponse(BaseModel):
    """Response model for a deployment"""
    id: str
    flow_id: str
    name: str
    version: str
    status: str
    endpoint_url: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    settings: Dict[str, Any] = {}

class DeploymentListResponse(BaseModel):
    """Response model for listing deployments"""
    items: List[DeploymentResponse]
    total: int
