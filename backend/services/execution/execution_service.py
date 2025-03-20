# backend/services/execution/execution_service.py
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import logging
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
        
        # Determine framework to use
        if not framework:
            # If no framework specified, use the one from the flow or default to langgraph
            framework = flow.framework if hasattr(flow, 'framework') and flow.framework else "langgraph"
        
        # Check if framework is supported
        if framework not in self.adapter_registry:
            raise ValueError(f"Framework {framework} is not supported")
        
        # Get adapter
        adapter = self.adapter_registry[framework]
        
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
            flow_config = flow.to_dict()
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
