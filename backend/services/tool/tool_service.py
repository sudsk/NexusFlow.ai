# backend/services/tool/tool_service.py
from typing import Dict, List, Any, Optional
from ...db.repositories.tool_repository import ToolRepository

class ToolService:
    """Service for managing tools"""
    
    def __init__(self, tool_repository: ToolRepository):
        self.tool_repository = tool_repository
    
    async def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools"""
        tools = self.tool_repository.get_all()
        return [tool.to_dict() for tool in tools]
    
    async def get_tool_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a tool by name"""
        tool = self.tool_repository.get_by_name(name)
        return tool.to_dict() if tool else None
    
    async def register_tool(self, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new tool"""
        tool = self.tool_repository.create(tool_data)
        return tool.to_dict()
