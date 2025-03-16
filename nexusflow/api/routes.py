"""
API routes for NexusFlow.ai

This module defines the FastAPI routes for the NexusFlow API, which allows clients
to create, manage, and execute flows.
"""

from typing import Dict, List, Any, Optional
import logging
import uuid
from datetime import datetime
import json
import asyncio

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, status, Query, Path, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from nexusflow.api.models import (
    AgentConfig,
    FlowConfig,
    ExecuteRequest,
    ExecuteResponse,
    CapabilityDefinition,
    FlowCreateRequest,
    FlowResponse,
    DeployRequest,
    DeployResponse,
    FlowExecutionRequest,
    FlowExecutionResponse,
    SearchFlowsRequest,
    WebhookConfig,
    ErrorResponse
)
from nexusflow.core import (
    Agent, 
    Flow, 
    CapabilityType, 
    capability_registry
)
from nexusflow.agents import (
    ReasoningAgent,
    RetrievalAgent,
    CodingAgent,
    AnalysisAgent
)
from nexusflow.graph import DynamicGraphBuilder
from nexusflow.db.session import get_db
from nexusflow.db.repositories import (
    FlowRepository, 
    ExecutionRepository,
    DeploymentRepository,
    WebhookRepository
)

# Get router from __init__.py
from nexusflow.api import router

logger = logging.getLogger(__name__)

def validate_api_key(api_key: str, db: Session = Depends(get_db)):
    """
    Validate API key
    
    Args:
        api_key: API key
        db: Database session        
        
    Returns:
        API key if valid
        
    Raises:
        HTTPException: If API key is invalid
    """
    # For development, accept any non-empty key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required"
        )
    
    # Check for API key format
    if not api_key.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format. Must start with 'Bearer '"
        )
    
    # Extract key
    key = api_key.replace("Bearer ", "")
    
    # Check if key is valid
    deployment_repo = DeploymentRepository(db)
    deployment = deployment_repo.get_by_api_key(key)
    
    if not deployment or deployment.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return key
    
#
# Flow execution endpoint
#
@router.post("/execute", response_model=ExecuteResponse)
async def execute_flow(request: ExecuteRequest):
    """
    Execute a flow with the given configuration and input
    
    This endpoint allows executing a flow without first creating it.
    
    Args:
        request: Execute request with flow configuration and input
        
    Returns:
        Results of the flow execution
    """
    try:
        # Create agents from the configuration
        agents = []
        for agent_config in request.flow_config.agents:
            # Create appropriate agent type based on capabilities
            agent = create_agent_from_config(agent_config)
            agents.append(agent)
        
        # Create flow from the configuration
        flow = Flow(
            name=request.flow_config.name,
            description=request.flow_config.description,
            agents=agents,
            max_steps=request.flow_config.max_steps,
            tools=request.flow_config.tools
        )
        
        # Execute flow
        result = await flow.execute(request.input)
        
        # Return result
        return ExecuteResponse(
            flow_id=flow.flow_id,
            output=result.get("output", {}).to_dict() if hasattr(result.get("output", {}), "to_dict") else result.get("output", {}),
            steps=result.get("steps", 0),
            execution_trace=result.get("execution_trace", []),
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.exception(f"Error executing flow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

#
# Capabilities endpoint
#
@router.get("/capabilities", response_model=List[CapabilityDefinition])
async def get_capabilities():
    """
    Get all available capabilities
    
    Returns:
        List of capability definitions
    """
    try:
        # Get all capability definitions from the registry
        capabilities = []
        for capability_type in CapabilityType.all():
            definition = capability_registry.get_capability_definition(capability_type)
            if definition:
                capabilities.append(CapabilityDefinition(
                    type=definition.type,
                    name=definition.name,
                    description=definition.description,
                    parameters=definition.parameters,
                    requires_tools=definition.requires_tools,
                    provides_output=definition.provides_output,
                    requires_input=definition.requires_input,
                    examples=definition.examples
                ))
        
        return capabilities
    
    except Exception as e:
        logger.exception(f"Error getting capabilities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

#
# Input analysis endpoint
#
@router.post("/analyze-input", response_model=List[str])
async def analyze_input(input_data: Dict[str, Any]):
    """
    Analyze input to determine required capabilities
    
    Args:
        input_data: Input data to analyze
        
    Returns:
        List of required capability types
    """
    try:
        # Analyze input to determine required capabilities
        required_capabilities = capability_registry.analyze_required_capabilities(input_data)
        
        return required_capabilities
    
    except Exception as e:
        logger.exception(f"Error analyzing input: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

#
# Flow management endpoints
#
@router.post("/flows", response_model=FlowResponse, status_code=status.HTTP_201_CREATED)
async def create_flow(
    request: FlowCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new flow
    
    Args:
        request: Flow creation request
        db: Database session        
        
    Returns:
        Created flow
    """
    try:
        # Create repository
        repository = FlowRepository(db)
        
        # Prepare flow data
        flow_data = {
            "name": request.flow_config.name,
            "description": request.flow_config.description,
            "config": request.flow_config.model_dump()
        }
        
        # Create flow in database
        flow = repository.create(flow_data)
        
        # Return flow data
        return FlowResponse(
            id=flow.id,
            name=flow.name,
            description=flow.description,
            created_at=flow.created_at,
            updated_at=flow.updated_at,
            config=FlowConfig(**flow.config)
        )
    
    except Exception as e:
        logger.exception(f"Error creating flow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/flows", response_model=List[FlowResponse])
async def list_flows(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List flows
    
    Args:
        limit: Maximum number of flows to return
        offset: Number of flows to skip
        name: Filter by name (optional)
        db: Database session        
        
    Returns:
        List of flows
    """
    try:
        # Get repository
        repository = FlowRepository(db)

        # Get flows from database
        flows = repository.get_all(skip=offset, limit=limit, name=name)
        
        # Convert to response models
        return [
            FlowResponse(
                id=flow.id,
                name=flow.name,
                description=flow.description,
                created_at=flow.created_at,
                updated_at=flow.updated_at,
                config=FlowConfig(**flow.config)
            )
            for flow in flows
        ]
    
    except Exception as e:
        logger.exception(f"Error listing flows: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/flows/{flow_id}", response_model=FlowResponse)
async def get_flow(
    flow_id: str = Path(...),
    db: Session = Depends(get_db)
):
    """
    Get a specific flow
    
    Args:
        flow_id: ID of the flow
        db: Database session        
        
    Returns:
        Flow details
    """
    try:
        # Get repository
        repository = FlowRepository(db)
        
        # Get flow from database
        flow = repository.get_by_id(flow_id)
        
        if not flow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flow with ID {flow_id} not found"
            )
        
        # Convert to response model
        return FlowResponse(
            id=flow.id,
            name=flow.name,
            description=flow.description,
            created_at=flow.created_at,
            updated_at=flow.updated_at,
            config=FlowConfig(**flow.config)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting flow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/flows/{flow_id}", response_model=FlowResponse)
async def update_flow(
    request: FlowCreateRequest,
    flow_id: str = Path(...),
    db: Session = Depends(get_db)
):
    """
    Update a flow
    
    Args:
        request: Flow update request
        flow_id: ID of the flow
        db: Database session        
        
    Returns:
        Updated flow
    """
    try:
        # Get repository
        repository = FlowRepository(db)
        
        # Check if flow exists
        flow = repository.get_by_id(flow_id)
                                    
        if not flow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flow with ID {flow_id} not found"
            )
        
        # Update flow data
        flow_data = {
            "name": request.flow_config.name,
            "description": request.flow_config.description,
            "config": request.flow_config.model_dump(),
            "updated_at": datetime.utcnow()
        }
        
        # Update flow in database
        updated_flow = repository.update(flow_id, flow_data)

        # Convert to response model
        return FlowResponse(
            id=updated_flow.id,
            name=updated_flow.name,
            description=updated_flow.description,
            created_at=updated_flow.created_at,
            updated_at=updated_flow.updated_at,
            config=FlowConfig(**updated_flow.config)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error updating flow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/flows/{flow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_flow(
    flow_id: str = Path(...),
    db: Session = Depends(get_db)
):
    """
    Delete a flow
    
    Args:
        flow_id: ID of the flow
        db: Database session        
    """
    try:
        # Get repository
        repository = FlowRepository(db)
        
        # Check if flow exists
        flow = repository.get_by_id(flow_id)
        if not flow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flow with ID {flow_id} not found"
            )
        
        # Delete flow from database
        success = repository.delete(flow_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete flow with ID {flow_id}"
            )
        
        # Return no content
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting flow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/flows/{flow_id}/execute", response_model=FlowExecutionResponse)
async def execute_flow_by_id(
    request: FlowExecutionRequest,
    background_tasks: BackgroundTasks,
    flow_id: str = Path(...)
):
    """
    Execute a flow by ID
    
    Args:
        request: Flow execution request
        background_tasks: FastAPI background tasks
        flow_id: ID of the flow
        
    Returns:
        Flow execution information
    """
    try:
        if flow_id not in flows_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flow with ID {flow_id} not found"
            )
        
        # Get flow configuration
        flow_data = flows_db[flow_id]
        flow_config = FlowConfig(**flow_data["config"])
        
        # Generate execution ID
        execution_id = str(uuid.uuid4())
        
        # Create execution record
        execution_data = {
            "id": execution_id,
            "flow_id": flow_id,
            "status": "pending",
            "started_at": datetime.utcnow(),
            "completed_at": None,
            "input": request.input,
            "result": None,
            "error": None
        }
        
        executions_db[execution_id] = execution_data
        
        # Execute flow in background
        background_tasks.add_task(
            execute_flow_background,
            flow_id=flow_id,
            execution_id=execution_id,
            input_data=request.input,
            options=request.options or {}
        )
        
        return FlowExecutionResponse(
            execution_id=execution_id,
            status="pending",
            result=None,
            error=None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error executing flow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/executions/{execution_id}", response_model=FlowExecutionResponse)
async def get_execution(execution_id: str = Path(...)):
    """
    Get execution details
    
    Args:
        execution_id: ID of the execution
        
    Returns:
        Execution details
    """
    try:
        if execution_id not in executions_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution with ID {execution_id} not found"
            )
        
        execution_data = executions_db[execution_id]
        
        return FlowExecutionResponse(
            execution_id=execution_id,
            status=execution_data["status"],
            result=execution_data["result"],
            error=execution_data["error"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting execution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

#
# Deployment endpoints
#
@router.post("/flows/{flow_id}/deploy", response_model=DeployResponse)
async def deploy_flow(
    request: DeployRequest,
    flow_id: str = Path(...)
):
    """
    Deploy a flow as an API endpoint
    
    Args:
        request: Deploy request
        flow_id: ID of the flow
        
    Returns:
        Deployment information
    """
    try:
        if flow_id not in flows_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flow with ID {flow_id} not found"
            )
        
        # Generate deployment ID and API key
        deployment_id = str(uuid.uuid4())
        api_key = f"nf_{uuid.uuid4().hex[:16]}"
        
        # Create endpoint URL
        endpoint_url = f"/api/nexusflow/deployed/{request.version}/{deployment_id}/execute"
        
        # Create deployment record
        deployment_data = {
            "id": deployment_id,
            "flow_id": flow_id,
            "version": request.version,
            "description": request.description or flows_db[flow_id]["description"],
            "api_key": api_key,
            "endpoint_url": endpoint_url,
            "status": "active",
            "deployed_at": datetime.utcnow().isoformat(),
            "webhooks": []
        }
        
        deployments_db[deployment_id] = deployment_data
        
        return DeployResponse(
            deployment_id=deployment_id,
            api_key=api_key,
            endpoint_url=endpoint_url,
            status="active",
            deployed_at=deployment_data["deployed_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deploying flow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/deployments/{deployment_id}/webhooks", response_model=Dict[str, Any])
async def create_webhook(
    config: WebhookConfig,
    deployment_id: str = Path(...)
):
    """
    Create a webhook for a deployment
    
    Args:
        config: Webhook configuration
        deployment_id: ID of the deployment
        
    Returns:
        Created webhook information
    """
    try:
        if deployment_id not in deployments_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deployment with ID {deployment_id} not found"
            )
        
        # Generate webhook ID
        webhook_id = str(uuid.uuid4())
        
        # Create webhook record
        webhook_data = {
            "id": webhook_id,
            "url": config.url,
            "events": config.events,
            "secret": config.secret,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Add to deployment
        deployments_db[deployment_id]["webhooks"].append(webhook_data)
        
        return webhook_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error creating webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/deployed/{version}/{deployment_id}/execute", response_model=FlowExecutionResponse)
async def execute_deployed_flow(
    request: FlowExecutionRequest,
    background_tasks: BackgroundTasks,
    version: str = Path(...),
    deployment_id: str = Path(...),
    api_key: str = Depends(validate_api_key)  # This would need to be implemented
):
    """
    Execute a deployed flow
    
    Args:
        request: Flow execution request
        background_tasks: FastAPI background tasks
        version: API version
        deployment_id: ID of the deployment
        api_key: API key for authentication
        
    Returns:
        Flow execution information
    """
    try:
        if deployment_id not in deployments_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deployment with ID {deployment_id} not found"
            )
        
        deployment_data = deployments_db[deployment_id]
        flow_id = deployment_data["flow_id"]
        
        if flow_id not in flows_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Flow with ID {flow_id} not found"
            )
        
        # Generate execution ID
        execution_id = str(uuid.uuid4())
        
        # Create execution record
        execution_data = {
            "id": execution_id,
            "flow_id": flow_id,
            "deployment_id": deployment_id,
            "status": "pending",
            "started_at": datetime.utcnow(),
            "completed_at": None,
            "input": request.input,
            "result": None,
            "error": None
        }
        
        executions_db[execution_id] = execution_data
        
        # Execute flow in background
        background_tasks.add_task(
            execute_flow_background,
            flow_id=flow_id,
            execution_id=execution_id,
            input_data=request.input,
            options=request.options or {},
            deployment_id=deployment_id
        )
        
        return FlowExecutionResponse(
            execution_id=execution_id,
            status="pending",
            result=None,
            error=None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error executing deployed flow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

#
# Helper functions
#
def create_agent_from_config(agent_config: AgentConfig) -> Agent:
    """
    Create an agent from configuration
    
    Args:
        agent_config: Agent configuration
        
    Returns:
        Created agent
    """
    capabilities = agent_config.capabilities
    
    # Determine the most appropriate agent type based on capabilities
    if CapabilityType.CODE_GENERATION.value in capabilities:
        return CodingAgent(
            name=agent_config.name,
            description=agent_config.description,
            model_provider=agent_config.model_provider,
            model_name=agent_config.model_name,
            system_message=agent_config.system_message,
            temperature=agent_config.temperature,
            max_tokens=agent_config.max_tokens,
            tool_names=agent_config.tool_names,
            can_delegate=agent_config.can_delegate
        )
    elif CapabilityType.DATA_ANALYSIS.value in capabilities:
        return AnalysisAgent(
            name=agent_config.name,
            description=agent_config.description,
            model_provider=agent_config.model_provider,
            model_name=agent_config.model_name,
            system_message=agent_config.system_message,
            temperature=agent_config.temperature,
            max_tokens=agent_config.max_tokens,
            tool_names=agent_config.tool_names,
            can_delegate=agent_config.can_delegate
        )
    elif CapabilityType.INFORMATION_RETRIEVAL.value in capabilities:
        return RetrievalAgent(
            name=agent_config.name,
            description=agent_config.description,
            model_provider=agent_config.model_provider,
            model_name=agent_config.model_name,
            system_message=agent_config.system_message,
            temperature=agent_config.temperature,
            max_tokens=agent_config.max_tokens,
            tool_names=agent_config.tool_names,
            can_delegate=agent_config.can_delegate
        )
    else:
        # Default to reasoning agent
        return ReasoningAgent(
            name=agent_config.name,
            description=agent_config.description,
            model_provider=agent_config.model_provider,
            model_name=agent_config.model_name,
            system_message=agent_config.system_message,
            temperature=agent_config.temperature,
            max_tokens=agent_config.max_tokens,
            tool_names=agent_config.tool_names,
            can_delegate=agent_config.can_delegate
        )

async def execute_flow_background(
    flow_id: str,
    execution_id: str,
    input_data: Dict[str, Any],
    options: Dict[str, Any] = None,
    deployment_id: Optional[str] = None
):
    """
    Execute a flow in the background
    
    Args:
        flow_id: ID of the flow
        execution_id: ID of the execution
        input_data: Input data for the flow
        options: Execution options
        deployment_id: ID of the deployment (if any)
    """
    options = options or {}
    
    try:
        # Update execution status
        execution_data = executions_db[execution_id]
        execution_data["status"] = "running"
        
        # Get flow configuration
        flow_data = flows_db[flow_id]
        flow_config = FlowConfig(**flow_data["config"])
        
        # Create agents from the configuration
        agents = []
        for agent_config in flow_config.agents:
            # Create appropriate agent type based on capabilities
            agent = create_agent_from_config(agent_config)
            agents.append(agent)
        
        # Create flow from the configuration
        flow = Flow(
            name=flow_config.name,
            description=flow_config.description,
            agents=agents,
            max_steps=flow_config.max_steps,
            tools=flow_config.tools
        )
        
        # Execute flow
        result = await flow.execute(input_data)
        
        # Update execution record
        execution_data["status"] = "completed"
        execution_data["completed_at"] = datetime.utcnow()
        execution_data["result"] = result
        
        # Send webhook notifications if this is a deployed flow
        if deployment_id:
            await send_webhook_notifications(
                deployment_id=deployment_id,
                execution_id=execution_id,
                status="completed",
                result=result
            )
    
    except Exception as e:
        logger.exception(f"Error executing flow in background: {str(e)}")
        
        # Update execution record with error
        if execution_id in executions_db:
            execution_data = executions_db[execution_id]
            execution_data["status"] = "failed"
            execution_data["completed_at"] = datetime.utcnow()
            execution_data["error"] = str(e)
            
            # Send webhook notifications if this is a deployed flow
            if deployment_id:
                await send_webhook_notifications(
                    deployment_id=deployment_id,
                    execution_id=execution_id,
                    status="failed",
                    error=str(e)
                )

async def send_webhook_notifications(
    deployment_id: str,
    execution_id: str,
    status: str,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
):
    """
    Send webhook notifications for an execution
    
    Args:
        deployment_id: ID of the deployment
        execution_id: ID of the execution
        status: Execution status
        result: Execution result (for completed executions)
        error: Error message (for failed executions)
    """
    try:
        if deployment_id not in deployments_db:
            logger.error(f"Deployment {deployment_id} not found for webhook notifications")
            return
        
        deployment = deployments_db[deployment_id]
        webhooks = deployment.get("webhooks", [])
        
        if not webhooks:
            return
        
        # Import httpx here to avoid circular imports
        import httpx
        import hmac
        import hashlib
        
        for webhook in webhooks:
            # Check if webhook should receive this event
            if status not in webhook["events"] and "all" not in webhook["events"]:
                continue
            
            # Prepare payload
            payload = {
                "execution_id": execution_id,
                "deployment_id": deployment_id,
                "flow_id": deployment["flow_id"],
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if status == "completed" and result:
                payload["result"] = result
            elif status == "failed" and error:
                payload["error"] = error
            
            # Add signature if secret is provided
            headers = {"Content-Type": "application/json"}
            
            if webhook.get("secret"):
                payload_bytes = json.dumps(payload).encode()
                signature = hmac.new(
                    webhook["secret"].encode(),
                    payload_bytes,
                    hashlib.sha256
                ).hexdigest()
                headers["X-NexusFlow-Signature"] = signature
            
            # Send webhook
            async with httpx.AsyncClient() as client:
                try:
                    await client.post(
                        webhook["url"],
                        json=payload,
                        headers=headers,
                        timeout=10.0
                    )
                except Exception as e:
                    logger.error(f"Error sending webhook to {webhook['url']}: {str(e)}")
    
    except Exception as e:
        logger.exception(f"Error sending webhook notifications: {str(e)}")


