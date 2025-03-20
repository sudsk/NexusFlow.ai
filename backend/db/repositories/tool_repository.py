# backend/db/repositories/tool_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
from datetime import datetime

from ..models.tool_model import ToolModel

class ToolRepository:
    """Repository for Tool entities"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        name_filter: Optional[str] = None,
        category: Optional[str] = None,
        enabled_only: bool = False
    ) -> List[ToolModel]:
        """
        Get all tools with optional filtering
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            name_filter: Filter by name or description
            category: Filter by category
            enabled_only: Only include enabled tools
            
        Returns:
            List of tool models
        """
        query = self.db.query(ToolModel)
        
        # Apply filters
        if name_filter:
            query = query.filter(or_(
                ToolModel.name.ilike(f"%{name_filter}%"),
                ToolModel.description.ilike(f"%{name_filter}%")
            ))
            
        if category:
            # Search in metadata JSON field for category
            # This is PostgreSQL specific syntax
            query = query.filter(ToolModel.metadata.contains({"category": category}))
            
        if enabled_only:
            query = query.filter(ToolModel.is_enabled == True)
            
        # Order by name
        query = query.order_by(ToolModel.name)
            
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, tool_id: str) -> Optional[ToolModel]:
        """Get a tool by ID"""
        return self.db.query(ToolModel).filter(ToolModel.id == tool_id).first()
    
    def get_by_name(self, name: str) -> Optional[ToolModel]:
        """Get a tool by name"""
        return self.db.query(ToolModel).filter(ToolModel.name == name).first()
    
    def create(self, tool_data: Dict[str, Any]) -> ToolModel:
        """Create a new tool"""
        tool = ToolModel(**tool_data)
        self.db.add(tool)
        self.db.commit()
        self.db.refresh(tool)
        return tool
    
    def update(self, tool_id: str, tool_data: Dict[str, Any]) -> Optional[ToolModel]:
        """Update an existing tool"""
        tool = self.get_by_id(tool_id)
        if not tool:
            return None
        
        # Update specified fields
        for key, value in tool_data.items():
            setattr(tool, key, value)
            
        # Always update the updated_at timestamp
        tool.updated_at = datetime.utcnow()
            
        self.db.commit()
        self.db.refresh(tool)
        return tool
    
    def delete(self, tool_id: str) -> bool:
        """Delete a tool"""
        tool = self.get_by_id(tool_id)
        if not tool:
            return False
        
        self.db.delete(tool)
        self.db.commit()
        return True
    
    def toggle_enabled(self, tool_id: str, enabled: bool) -> Optional[ToolModel]:
        """Toggle a tool's enabled status"""
        tool = self.get_by_id(tool_id)
        if not tool:
            return None
        
        tool.is_enabled = enabled
        tool.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(tool)
        return tool
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about tools"""
        # Total count
        total_count = self.db.query(ToolModel).count()
        
        # Enabled count
        enabled_count = self.db.query(ToolModel).filter(ToolModel.is_enabled == True).count()
        
        # Count by authentication requirement
        auth_required_count = self.db.query(ToolModel).filter(
            ToolModel.requires_authentication == True
        ).count()
        
        # Count tools by category
        # This is a simplified approach - in a real database you'd use a proper 
        # JSON field query based on your database type (PostgreSQL, MySQL, etc.)
        tools = self.db.query(ToolModel).all()
        categories = {}
        
        for tool in tools:
            if hasattr(tool, 'metadata') and tool.metadata:
                metadata = tool.metadata
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except (json.JSONDecodeError, TypeError):
                        metadata = {}
                
                category = metadata.get('category', 'uncategorized')
                categories[category] = categories.get(category, 0) + 1
        
        return {
            "total": total_count,
            "enabled": enabled_count,
            "auth_required": auth_required_count,
            "categories": categories
        }
    
    def search_by_metadata(
        self,
        metadata_query: Dict[str, Any],
        skip: int = 0,
        limit: int = 100
    ) -> List[ToolModel]:
        """
        Search tools by metadata fields
        
        Args:
            metadata_query: Dictionary of metadata fields to match
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching tool models
        """
        # This is a simplified approach - in a real database you'd use a proper 
        # JSON field query based on your database type (PostgreSQL, MySQL, etc.)
        query = self.db.query(ToolModel)
        
        for key, value in metadata_query.items():
            # PostgreSQL specific JSON containment operator
            query = query.filter(ToolModel.metadata.contains({key: value}))
            
        return query.offset(skip).limit(limit).all()
    
    def get_recently_updated(self, limit: int = 10) -> List[ToolModel]:
        """Get recently updated tools"""
        return self.db.query(ToolModel)\
            .order_by(desc(ToolModel.updated_at))\
            .limit(limit).all()
    
    def get_by_framework(self, framework: str, enabled_only: bool = True) -> List[ToolModel]:
        """
        Get tools compatible with a specific framework
        
        Args:
            framework: Framework name to check compatibility
            enabled_only: Only include enabled tools
            
        Returns:
            List of compatible tool models
        """
        # This would typically use a database-specific JSON query
        # For PostgreSQL, we'd use the ? operator or similar
        # For simplicity, we'll load all tools and filter in Python
        query = self.db.query(ToolModel)
        
        if enabled_only:
            query = query.filter(ToolModel.is_enabled == True)
            
        all_tools = query.all()
        
        compatible_tools = []
        for tool in all_tools:
            if hasattr(tool, 'metadata') and tool.metadata:
                metadata = tool.metadata
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except (json.JSONDecodeError, TypeError):
                        metadata = {}
                
                compatible_frameworks = metadata.get('compatible_frameworks', [])
                if not compatible_frameworks or framework in compatible_frameworks:
                    compatible_tools.append(tool)
        
        return compatible_tools
