# backend/services/execution/execution_service.py
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import logging
import json
from ...db.repositories.flow_repository import FlowRepository
from ...db.repositories.execution_repository import ExecutionRepository
from ...adapters.registry import get_adapter_registry

logger = logging.getLogger(__name__)

class ExecutionService:
    """Service for executing flows"""
    
    def __init__(self, flow_repository: FlowRepository, execution_repository: ExecutionRepository):
        self.flow_repository = flow_repository
        self.execution_repository = execution_repository
        self.adapter_registry = get_adapter_registry()
    
    async def execute_flow(
        self, 
        flow_id: str, 
        input_data: Dict[str, Any],
        framework: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a flow
        
        Args:
            flow_id: ID of the flow
            input_data: Input data for execution
            framework: Framework to use for execution (default is decided by flow)
            
        Returns:
            Execution results
        """
        # Get flow
        flow = self.flow_repository.get_by_id(flow_id)
        if not flow:
            raise ValueError(f"Flow with ID {flow_id} not found")
        
        # Extract flow config from database model
        flow_config = {}
        if hasattr(flow, 'config') and flow.config:
            flow_config = flow.config
        else:
            # Construct config from model fields
            flow_config = {
                "name": flow.name,
                "description": flow.description,
                "agents": [],  # This would need to be populated from a separate agents table
                "max_steps": getattr(flow, 'max_steps', 10),
                "tools": {}  # This would need to be populated from a tools table
            }
        
        # Determine framework to use
        if not framework:
            # If no framework specified, use the one from the flow or default to langgraph
            framework = flow_config.get("framework", "langgraph")
        
        # Check if framework is supported
        adapter_registry = get_adapter_registry()
        try:
            adapter = adapter_registry.get_adapter(framework)
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
        
        execution = self.execution_repository.create(execution_data)
        
        try:
            # Convert flow config to framework-specific format
            framework_flow = adapter.convert_flow(flow_config)
            
            # Update execution status
            self.execution_repository.update(
                execution_id, 
                {"status": "running"}
            )
            
            # Execute flow
            result = await adapter.execute_flow(framework_flow, input_data)
            
            # Update execution record with results
            self.execution_repository.update(
                execution_id,
                {
                    "status": "completed",
                    "completed_at": datetime.utcnow(),
                    "result": result,
                    "execution_trace": result.get("execution_trace", [])
                }
            )
            
            return {
                "execution_id": execution_id,
                "status": "completed",
                "result": result
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
            
            raise
    
    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get execution details
        
        Args:
            execution_id: ID of the execution
            
        Returns:
            Execution details or None if not found
        """
        execution = self.execution_repository.get_by_id(execution_id)
        if not execution:
            return None
            
        return self._convert_to_dict(execution)
    
    async def get_flow_executions(self, flow_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get executions for a flow
        
        Args:
            flow_id: ID of the flow
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of execution dictionaries
        """
        executions = self.execution_repository.get_by_flow_id(flow_id, skip, limit)
        return [self._convert_to_dict(execution) for execution in executions]
    
    async def get_recent_executions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent executions across all flows
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            List of execution dictionaries
        """
        executions = self.execution_repository.get_recent_executions(limit)
        return [self._convert_to_dict(execution) for execution in executions]
    
    async def get_execution_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics
        
        Returns:
            Dictionary of execution statistics
        """
        return self.execution_repository.get_stats()
    
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
        
        return {
            "id": execution.id,
            "flow_id": execution.flow_id,
            "framework": execution.framework,
            "status": execution.status,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "input": input_data,
            "result": result,
            "error": execution.error,
            "execution_trace": execution_trace
        }
