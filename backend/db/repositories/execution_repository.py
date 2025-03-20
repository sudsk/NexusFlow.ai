# backend/db/repositories/execution_repository.py
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, desc
from sqlalchemy.orm import Session

from ..models.flow_model import ExecutionModel

class ExecutionRepository:
    """Repository for Execution entities"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, execution_id: str) -> Optional[ExecutionModel]:
        """Get an execution by ID"""
        return self.db.query(ExecutionModel).filter(ExecutionModel.id == execution_id).first()
    
    def get_by_flow_id(
        self, 
        flow_id: str, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[ExecutionModel]:
        """Get executions for a flow with optional status filter"""
        query = self.db.query(ExecutionModel).filter(ExecutionModel.flow_id == flow_id)
        
        if status:
            query = query.filter(ExecutionModel.status == status)
            
        return query.order_by(desc(ExecutionModel.started_at)).offset(skip).limit(limit).all()
    
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
    
    def delete(self, execution_id: str) -> bool:
        """Delete an execution"""
        execution = self.get_by_id(execution_id)
        if not execution:
            return False
        
        self.db.delete(execution)
        self.db.commit()
        return True
    
    def get_recent_executions(self, limit: int = 10) -> List[ExecutionModel]:
        """Get recent executions across all flows"""
        return self.db.query(ExecutionModel)\
            .order_by(desc(ExecutionModel.started_at))\
            .limit(limit).all()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        total_count = self.db.query(ExecutionModel).count()
        completed_count = self.db.query(ExecutionModel).filter(ExecutionModel.status == "completed").count()
        failed_count = self.db.query(ExecutionModel).filter(ExecutionModel.status == "failed").count()
        cancelled_count = self.db.query(ExecutionModel).filter(ExecutionModel.status == "cancelled").count()
        running_count = self.db.query(ExecutionModel).filter(
            ExecutionModel.status.in_(["running", "pending"])
        ).count()
        
        success_rate = 0
        if (completed_count + failed_count + cancelled_count) > 0:
            success_rate = (completed_count / (completed_count + failed_count + cancelled_count)) * 100
            
        # Get average duration for completed executions
        duration_query = self.db.query(
            func.avg(ExecutionModel.completed_at - ExecutionModel.started_at)
        ).filter(
            ExecutionModel.status == "completed",
            ExecutionModel.completed_at.isnot(None)
        )
        
        avg_duration_seconds = duration_query.scalar()
        avg_duration = None
        if avg_duration_seconds:
            avg_duration = round(avg_duration_seconds.total_seconds(), 2)
            
        return {
            "total_executions": total_count,
            "completed_executions": completed_count,
            "failed_executions": failed_count,
            "cancelled_executions": cancelled_count,
            "running_executions": running_count,
            "success_rate": round(success_rate, 2),
            "avg_duration_seconds": avg_duration
        }
    
    def get_stats_by_period(self, period: str = "week") -> Dict[str, Any]:
        """
        Get execution statistics for a specific time period
        
        Args:
            period: Time period ('day', 'week', 'month')
        
        Returns:
            Dictionary with statistics for the period
        """
        # Determine time range based on period
        now = datetime.utcnow()
        if period == "day":
            start_date = now - timedelta(days=1)
        elif period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        else:
            start_date = now - timedelta(days=7)  # Default to week
            
        # Base query for the time period
        base_query = self.db.query(ExecutionModel).filter(
            ExecutionModel.started_at >= start_date
        )
        
        # Get counts by status
        total_count = base_query.count()
        completed_count = base_query.filter(ExecutionModel.status == "completed").count()
        failed_count = base_query.filter(ExecutionModel.status == "failed").count()
        cancelled_count = base_query.filter(ExecutionModel.status == "cancelled").count()
        
        # Calculate success rate
        success_rate = 0
        if (completed_count + failed_count + cancelled_count) > 0:
            success_rate = (completed_count / (completed_count + failed_count + cancelled_count)) * 100
        
        # Get executions by framework
        framework_counts = {}
        frameworks_query = self.db.query(
            ExecutionModel.framework, 
            func.count(ExecutionModel.id)
        ).filter(
            ExecutionModel.started_at >= start_date
        ).group_by(ExecutionModel.framework)
        
        for framework, count in frameworks_query.all():
            framework_counts[framework] = count
            
        # Get average duration for completed executions in the period
        duration_query = self.db.query(
            func.avg(ExecutionModel.completed_at - ExecutionModel.started_at)
        ).filter(
            ExecutionModel.status == "completed",
            ExecutionModel.completed_at.isnot(None),
            ExecutionModel.started_at >= start_date
        )
        
        avg_duration_seconds = duration_query.scalar()
        avg_duration = None
        if avg_duration_seconds:
            avg_duration = round(avg_duration_seconds.total_seconds(), 2)
            
        return {
            "period": period,
            "total_executions": total_count,
            "completed_executions": completed_count,
            "failed_executions": failed_count,
            "cancelled_executions": cancelled_count,
            "success_rate": round(success_rate, 2),
            "framework_counts": framework_counts,
            "avg_duration_seconds": avg_duration
        }
    
    def search_executions(
        self,
        search_query: Optional[str] = None,
        status: Optional[str] = None,
        framework: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ExecutionModel]:
        """
        Search executions with various filters
        
        Args:
            search_query: Text to search in execution data
            status: Filter by execution status
            framework: Filter by framework
            start_date: Filter executions after this date
            end_date: Filter executions before this date
            skip: Number of results to skip
            limit: Maximum number of results to return
            
        Returns:
            List of matching executions
        """
        query = self.db.query(ExecutionModel)
        
        # Apply filters
        if search_query:
            # Search in input and result data
            query = query.filter(
                or_(
                    ExecutionModel.input.cast(str).ilike(f"%{search_query}%"),
                    ExecutionModel.result.cast(str).ilike(f"%{search_query}%")
                )
            )
            
        if status:
            query = query.filter(ExecutionModel.status == status)
            
        if framework:
            query = query.filter(ExecutionModel.framework == framework)
            
        if start_date:
            query = query.filter(ExecutionModel.started_at >= start_date)
            
        if end_date:
            query = query.filter(ExecutionModel.started_at <= end_date)
            
        # Order by start date, newest first
        query = query.order_by(desc(ExecutionModel.started_at))
        
        # Apply pagination
        return query.offset(skip).limit(limit).all()
    
    def count_executions(
        self,
        search_query: Optional[str] = None,
        status: Optional[str] = None,
        framework: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        Count executions matching filters without pagination
        
        Args:
            Same filters as search_executions
            
        Returns:
            Count of matching executions
        """
        query = self.db.query(func.count(ExecutionModel.id))
        
        # Apply same filters as search
        if search_query:
            query = query.filter(
                or_(
                    ExecutionModel.input.cast(str).ilike(f"%{search_query}%"),
                    ExecutionModel.result.cast(str).ilike(f"%{search_query}%")
                )
            )
            
        if status:
            query = query.filter(ExecutionModel.status == status)
            
        if framework:
            query = query.filter(ExecutionModel.framework == framework)
            
        if start_date:
            query = query.filter(ExecutionModel.started_at >= start_date)
            
        if end_date:
            query = query.filter(ExecutionModel.started_at <= end_date)
            
        return query.scalar() or 0
