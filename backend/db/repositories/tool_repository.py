# backend/db/repositories/tool_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..models.tool_model import ToolModel

class ToolRepository:
    """Repository for Tool entities"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, skip: int = 0, limit: int = 100, name_filter: Optional[str] = None) -> List[ToolModel]:
        """Get all tools with optional filtering"""
        query = self.db.query(ToolModel)
        
        if name_filter:
            query = query.filter(or_(
                ToolModel.name.ilike(f"%{name_filter}%"),
                ToolModel.description.ilike(f"%{name_filter}%")
            ))
            
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
        
        for key, value in tool_data.items():
            setattr(tool, key, value)
            
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
