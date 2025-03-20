# backend/api/models/tool_models.py
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class ToolParameterSchema(BaseModel):
    """Schema for a tool parameter"""
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None

class ToolCreateRequest(BaseModel):
    """Request model for creating a tool"""
    name: str
    description: str
    parameters: Dict[str, Dict[str, Any]]
    function_name: Optional[str] = None
    is_enabled: bool = True
    requires_authentication: bool = False
    metadata: Optional[Dict[str, Any]] = None

class ToolUpdateRequest(BaseModel):
    """Request model for updating a tool"""
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Dict[str, Any]]] = None
    function_name: Optional[str] = None
    is_enabled: Optional[bool] = None
    requires_authentication: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

class ToolResponse(BaseModel):
    """Response model for a tool"""
    id: str
    name: str
    description: str
    parameters: Dict[str, Dict[str, Any]]
    function_name: Optional[str] = None
    is_enabled: bool
    requires_authentication: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class ToolListResponse(BaseModel):
    """Response model for listing tools"""
    items: List[ToolResponse]
    total: int
