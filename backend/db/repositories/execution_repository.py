# backend/db/repositories/execution_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from ..models.flow_model import ExecutionModel

class ExecutionRepository:
    """Repository for Execution entities"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, execution_id: str) -> Optional[ExecutionModel]:
        """Get an execution by ID"""
        return self.db.query(ExecutionModel).filter(ExecutionModel.id == execution_id).first()
    
    def get_by_flow_id(self, flow_id: str, skip: int = 0, limit: int = 100) -> List[ExecutionModel]:
        """Get executions for a flow"""
        return self.db.query(ExecutionModel)\
            .filter(ExecutionModel.flow_id == flow_id)\
            .order_by(ExecutionModel.started_at.desc())\
            .offset(skip).limit(limit).all()
    
    def create(self, execution_data: Dict[str, Any]) -> ExecutionModel:
        """Create a new execution"""
        execution = ExecutionModel(**execution_data)
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution
    
    def update(self, execution_id: str, execution_data: Dict[str, Any]) -> Optional[ExecutionModel]:
        """Update an execution"""
        execution = self.get_by_id(execution_id)
        if not execution:
            return None
        
        for key, value in execution_data.items():
            setattr(execution, key, value)
            
        self.db.commit()
        self.db.refresh(execution)
        return execution
    
    def get_recent_executions(self, limit: int = 10) -> List[ExecutionModel]:
        """Get recent executions across all flows"""
        return self.db.query(ExecutionModel)\
            .order_by(ExecutionModel.started_at.desc())\
            .limit(limit).all()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        total_count = self.db.query(ExecutionModel).count()
        completed_count = self.db.query(ExecutionModel).filter(ExecutionModel.status == "completed").count()
        failed_count = self.db.query(ExecutionModel).filter(ExecutionModel.status == "failed").count()
        
        success_rate = 0
        if total_count > 0:
            success_rate = (completed_count / total_count) * 100
            
        return {
            "total_executions": total_count,
            "completed_executions": completed_count,
            "failed_executions": failed_count,
            "success_rate": round(success_rate, 2)
        }
