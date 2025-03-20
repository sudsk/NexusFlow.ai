# backend/services/tool/tool_service.py
from typing import Dict, List, Any, Optional
from ...db.repositories.tool_repository import ToolRepository

class ToolService:
    """Service for managing tools"""
    
    def __init__(self, tool_repository: ToolRepository):
        self.tool_repository = tool_repository
    
    async def get_all_tools(self, skip: int = 0, limit: int = 100, name_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all available tools
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            name_filter: Optional filter for tool name or description
            
        Returns:
            List of tool dictionaries
        """
        tools = self.tool_repository.get_all(skip, limit, name_filter)
        return [self._convert_to_dict(tool) for tool in tools]
    
    async def get_tool_by_id(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a tool by ID
        
        Args:
            tool_id: ID of the tool
            
        Returns:
            Tool dictionary or None if not found
        """
        tool = self.tool_repository.get_by_id(tool_id)
        return self._convert_to_dict(tool) if tool else None
    
    async def get_tool_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a tool by name
        
        Args:
            name: Name of the tool
            
        Returns:
            Tool dictionary or None if not found
        """
        tool = self.tool_repository.get_by_name(name)
        return self._convert_to_dict(tool) if tool else None
    
    async def create_tool(self, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new tool
        
        Args:
            tool_data: Tool data
            
        Returns:
            Created tool dictionary
        """
        # Ensure parameters is a valid JSON object
        if "parameters" not in tool_data or not isinstance(tool_data["parameters"], dict):
            tool_data["parameters"] = {}
            
        tool = self.tool_repository.create(tool_data)
        return self._convert_to_dict(tool)
    
    async def update_tool(self, tool_id: str, tool_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing tool
        
        Args:
            tool_id: ID of the tool
            tool_data: Updated tool data
            
        Returns:
            Updated tool dictionary or None if not found
        """
        tool = self.tool_repository.update(tool_id, tool_data)
        return self._convert_to_dict(tool) if tool else None
    
    async def delete_tool(self, tool_id: str) -> bool:
        """
        Delete a tool
        
        Args:
            tool_id: ID of the tool
            
        Returns:
            True if deleted, False if not found
        """
        return self.tool_repository.delete(tool_id)
    
    def _convert_to_dict(self, tool) -> Dict[str, Any]:
        """Convert tool model to dictionary"""
        return {
            "id": tool.id,
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
            "function_name": tool.function_name,
            "is_enabled": tool.is_enabled,
            "requires_authentication": tool.requires_authentication,
            "created_at": tool.created_at.isoformat() if tool.created_at else None,
            "updated_at": tool.updated_at.isoformat() if tool.updated_at else None,
            "metadata": tool.metadata or {}
        }
