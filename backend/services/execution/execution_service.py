// backend/services/execution/execution_service.py
import uuid
import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List

from ...db.repositories.flow_repository import FlowRepository
from ...db.repositories.execution_repository import ExecutionRepository
from ...adapters.registry import get_adapter_registry

logger = logging.getLogger(__name__)

class ExecutionService:
    """Service for executing flows and managing execution state"""
    
    def __init__(self, flow_repository: FlowRepository, execution_repository: ExecutionRepository):
        self.flow_repository = flow_repository
        self.execution_repository = execution_repository
        self.adapter_registry = get_adapter_registry()
        self._active_executions = {}  # Store references to active executions
    
    async def execute_flow(
        self, 
        flow_id: str, 
        input_data: Dict[str, Any],
        framework: Optional[str] = None,
        streaming: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a flow with the given input data
        
        Args:
            flow_id: ID of the flow to execute
            input_data: Input data for the flow
            framework: Framework to use for execution (default is decided by flow)
            streaming: Whether to stream execution updates
            
        Returns:
            Dictionary containing execution details
        """
        # Get flow configuration
        flow = self.flow_repository.get_by_id(flow_id)
        if not flow:
            raise ValueError(f"Flow with ID {flow_id} not found")
        
        # Determine framework to use
        if not framework:
            framework = flow.framework
        
        # Check if framework is supported
        try:
            adapter = self.adapter_registry.get_adapter(framework)
        except ValueError:
            raise ValueError(f"Framework '{framework}' is not supported")
        
        # Create execution record
        execution_id = str(uuid.uuid4())
        execution_data = {
            "id": execution_id,
            "flow_id": flow_id,
            "framework": framework,
            "status": "pending",
            "started_at": datetime.utcnow(),
            "input": input_data
        }
        
        # Store execution in database
        execution = self.execution_repository.create(execution_data)
        
        # For streaming mode, start execution in background
        if streaming:
            asyncio.create_task(self._execute_flow_task(
                execution_id=execution_id,
                flow=flow,
                adapter=adapter,
                input_data=input_data
            ))
            
            return {
                "execution_id": execution_id,
                "status": "pending",
                "flow_id": flow_id,
                "framework": framework,
                "streaming": True
            }
        
        # For non-streaming mode, execute synchronously
        try:
            # Update execution status
            self.execution_repository.update(
                execution_id,
                {"status": "running"}
            )
            
            # Convert flow to framework-specific format
            flow_dict = flow.to_dict()
            framework_flow = adapter.convert_flow(flow_dict)
            
            # Execute flow
            result = await adapter.execute_flow(framework_flow, input_data)
            
            # Update execution record with success
            completed_at = datetime.utcnow()
            execution_trace = result.get("execution_trace", [])
            steps = len(execution_trace)
            
            self.execution_repository.update(
                execution_id,
                {
                    "status": "completed",
                    "completed_at": completed_at,
                    "result": result,
                    "execution_trace": execution_trace,
                    "steps": steps
                }
            )
            
            # Calculate execution time
            duration_seconds = (completed_at - execution.started_at).total_seconds()
            
            return {
                "execution_id": execution_id,
                "status": "completed",
                "result": result,
                "flow_id": flow_id,
                "framework": framework,
                "duration_seconds": duration_seconds,
                "steps": steps
            }
        except Exception as e:
            logger.exception(f"Error executing flow: {str(e)}")
            
            # Update execution record with error
            self.execution_repository.update(
                execution_id,
                {
                    "status": "failed",
                    "completed_at": datetime.utcnow(),
                    "error": str(e)
                }
            )
            
            # Re-raise exception
            raise
    
    async def _execute_flow_task(
        self,
        execution_id: str,
        flow: Any,
        adapter: Any,
        input_data: Dict[str, Any]
    ):
        """Background task for flow execution with streaming updates"""
        try:
            # Store reference to active execution
            self._active_executions[execution_id] = {
                "status": "running",
                "started_at": datetime.utcnow(),
                "current_step": 0,
                "current_trace": []
            }
            
            # Update execution status
            self.execution_repository.update(
                execution_id,
                {"status": "running"}
            )
            
            # Convert flow to framework-specific format
            flow_dict = flow.to_dict()
            framework_flow = adapter.convert_flow(flow_dict)
            
            # Prepare callback for streaming updates
            async def step_callback(step_data):
                # Update active execution state
                if execution_id in self._active_executions:
                    self._active_executions[execution_id]["current_step"] += 1
                    self._active_executions[execution_id]["current_trace"].append(step_data)
            
            # Execute flow with streaming callback
            result = await adapter.execute_flow(
                framework_flow, 
                input_data,
                step_callback=step_callback
            )
            
            # Update execution record with success
            completed_at = datetime.utcnow()
            execution_trace = result.get("execution_trace", [])
            steps = len(execution_trace)
            
            self.execution_repository.update(
                execution_id,
                {
                    "status": "completed",
                    "completed_at": completed_at,
                    "result": result,
                    "execution_trace": execution_trace,
                    "steps": steps
                }
            )
            
            # Clean up active execution reference
            if execution_id in self._active_executions:
                del self._active_executions[execution_id]
                
        except Exception as e:
            logger.exception(f"Error in background execution: {str(e)}")
            
            # Update execution record with error
            self.execution_repository.update(
                execution_id,
                {
                    "status": "failed",
                    "completed_at": datetime.utcnow(),
                    "error": str(e)
                }
            )
            
            # Clean up active execution reference
            if execution_id in self._active_executions:
                del self._active_executions[execution_id]
    
    async def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Get current status of an execution
        
        Args:
            execution_id: ID of the execution
        
        Returns:
            Dictionary containing execution status
        """
        # First check if it's an active streaming execution
        if execution_id in self._active_executions:
            active_exec = self._active_executions[execution_id]
            return {
                "execution_id": execution_id,
                "status": "running",
                "current_step": active_exec["current_step"],
                "current_trace": active_exec["current_trace"],
                "streaming": True
            }
        
        # Otherwise check the database
        execution = self.execution_repository.get_by_id(execution_id)
        if not execution:
            raise ValueError(f"Execution with ID {execution_id} not found")
        
        return self._convert_to_dict(execution)
    
    async def get_flow_executions(
        self,
        flow_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get executions for a flow with pagination
        
        Args:
            flow_id: ID of the flow
            skip: Number of executions to skip
            limit: Maximum number of executions to return
        
        Returns:
            List of execution dictionaries
        """
        executions = self.execution_repository.get_by_flow_id(flow_id, skip, limit)
        return [self._convert_to_dict(execution) for execution in executions]
    
    async def get_recent_executions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent executions across all flows
        
        Args:
            limit: Maximum number of executions to return
        
        Returns:
            List of execution dictionaries
        """
        executions = self.execution_repository.get_recent_executions(limit)
        return [self._convert_to_dict(execution) for execution in executions]
    
    async def get_execution_stats(
        self,
        time_period: str = "week"
    ) -> Dict[str, Any]:
        """
        Get execution statistics
        
        Args:
            time_period: Time period for statistics ('day', 'week', 'month')
        
        Returns:
            Dictionary of execution statistics
        """
        base_stats = self.execution_repository.get_stats()
        
        # Add time-period specific stats
        time_stats = self.execution_repository.get_stats_by_period(time_period)
        
        return {
            **base_stats,
            "period_stats": time_stats
        }
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel an active execution
        
        Args:
            execution_id: ID of the execution to cancel
        
        Returns:
            True if execution was cancelled, False otherwise
        """
        # Check if it's an active streaming execution
        if execution_id in self._active_executions:
            # Mark as cancelled in the database
            self.execution_repository.update(
                execution_id,
                {
                    "status": "cancelled",
                    "completed_at": datetime.utcnow(),
                    "error": "Execution cancelled by user"
                }
            )
            
            # Remove from active executions
            del self._active_executions[execution_id]
            return True
        
        # Check if it's in the database but not active
        execution = self.execution_repository.get_by_id(execution_id)
        if not execution:
            return False
        
        # Can only cancel running or pending executions
        if execution.status not in ["running", "pending"]:
            return False
        
        # Update status
        self.execution_repository.update(
            execution_id,
            {
                "status": "cancelled",
                "completed_at": datetime.utcnow(),
                "error": "Execution cancelled by user"
            }
        )
        
        return True
    
    async def delete_execution(self, execution_id: str) -> bool:
        """
        Delete an execution record
        
        Args:
            execution_id: ID of the execution to delete
        
        Returns:
            True if execution was deleted, False if not found
        """
        # Check if it's an active execution
        if execution_id in self._active_executions:
            # Can't delete active executions
            raise ValueError("Cannot delete an active execution")
        
        # Delete from database
        return self.execution_repository.delete(execution_id)
    
    def _convert_to_dict(self, execution) -> Dict[str, Any]:
        """Convert execution model to dictionary"""
        # Handle JSON fields that might be stored as strings
        result = execution.result
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except (json.JSONDecodeError, TypeError):
                result = {"raw": result}
                
        input_data = execution.input
        if isinstance(input_data, str):
            try:
                input_data = json.loads(input_data)
            except (json.JSONDecodeError, TypeError):
                input_data = {"raw": input_data}
                
        execution_trace = execution.execution_trace
        if isinstance(execution_trace, str):
            try:
                execution_trace = json.loads(execution_trace)
            except (json.JSONDecodeError, TypeError):
                execution_trace = []
        
        # Calculate duration if completed
        duration_seconds = None
        if execution.completed_at and execution.started_at:
            duration_seconds = (execution.completed_at - execution.started_at).total_seconds()
            
        # Format duration as string (e.g., "2m 30s")
        duration_str = None
        if duration_seconds is not None:
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            duration_str = f"{minutes}m {seconds}s"
        
        return {
            "id": execution.id,
            "flow_id": execution.flow_id,
            "framework": execution.framework,
            "status": execution.status,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "duration_seconds": duration_seconds,
            "duration": duration_str,
            "input": input_data,
            "result": result,
            "error": execution.error,
            "execution_trace": execution_trace,
            "steps": getattr(execution, 'steps', len(execution_trace) if execution_trace else 0)
        }
