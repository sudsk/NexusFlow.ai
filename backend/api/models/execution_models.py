# backend/api/models/execution_models.py
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class ExecutionRequest(BaseModel):
    """Request model for executing a flow"""
    flow_id: str
    input: Dict[str, Any]
    framework: Optional[str] = None

class ExecutionResponse(BaseModel):
    """Response model for execution results"""
    execution_id: str
    status: str
    result: Optional[Dict[str, Any]] = None

class ExecutionDetailsResponse(BaseModel):
    """Response model for detailed execution information"""
    id: str
    flow_id: str
    framework: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    input: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_trace: Optional[List[Dict[str, Any]]] = None

class ExecutionListResponse(BaseModel):
    """Response model for listing executions"""
    items: List[ExecutionDetailsResponse]
    total: int
