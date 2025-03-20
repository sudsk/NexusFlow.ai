# backend/api/routes/tool_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...services.tool.tool_service import ToolService
from ...db.repositories.tool_repository import ToolRepository
from ..models.tool_models import (
    ToolCreateRequest,
    ToolUpdateRequest,
    ToolResponse,
    ToolListResponse
)

router = APIRouter(prefix="/tools", tags=["tools"])

def get_tool_service(db: Session = Depends(get_db)):
    tool_repo = ToolRepository(db)
    return ToolService(tool_repo)

@router.post("/", response_model=ToolResponse)
async def create_tool(
    request: ToolCreateRequest,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Create a new tool"""
    try:
        # Check if a tool with the same name already exists
        existing_tool = await tool_service.get_tool_by_name(request.name)
        if existing_tool:
            raise HTTPException(
                status_code=400,
                detail=f"Tool with name '{request.name}' already exists"
            )
        
        tool = await tool_service.create_tool(request.dict())
        return tool
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(
    tool_id: str,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Get a tool by ID"""
    tool = await tool_service.get_tool_by_id(tool_id)
    
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool with ID {tool_id} not found")
    
    return tool

@router.put("/{tool_id}", response_model=ToolResponse)
async def update_tool(
    tool_id: str,
    request: ToolUpdateRequest,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Update a tool"""
    try:
        # Check if the tool exists
        existing_tool = await tool_service.get_tool_by_id(tool_id)
        if not existing_tool:
            raise HTTPException(
                status_code=404,
                detail=f"Tool with ID {tool_id} not found"
            )
        
        # Check if name is being changed and if it conflicts
        if request.name and request.name != existing_tool["name"]:
            tool_with_name = await tool_service.get_tool_by_name(request.name)
            if tool_with_name and tool_with_name["id"] != tool_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Tool with name '{request.name}' already exists"
                )
        
        # Update the tool
        updated_data = {k: v for k, v in request.dict().items() if v is not None}
        updated_tool = await tool_service.update_tool(tool_id, updated_data)
        
        if not updated_tool:
            raise HTTPException(
                status_code=404,
                detail=f"Tool with ID {tool_id} not found"
            )
        
        return updated_tool
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{tool_id}")
async def delete_tool(
    tool_id: str,
    tool_service: ToolService = Depends(get_tool_service)
):
    """Delete a tool"""
    success = await tool_service.delete_tool(tool_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Tool with ID {tool_id} not found")
    
    return {"message": f"Tool with ID {tool_id} successfully deleted"}

@router.get("/", response_model=ToolListResponse)
async def list_tools(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    name_filter: Optional[str] = None,
    tool_service: ToolService = Depends(get_tool_service)
):
    """List tools with optional filtering"""
    tools = await tool_service.get_all_tools(skip, limit, name_filter)
    
    return ToolListResponse(
        items=tools,
        total=len(tools)  # In a real implementation, this would be a count query
    )
