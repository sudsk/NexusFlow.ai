# backend/api/routes/execution_routes.py 
@router.get("/flow/{flow_id}", response_model=ExecutionListResponse)
async def get_flow_executions(
    flow_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    execution_service: ExecutionService = Depends(get_execution_service)
):
    """Get executions for a specific flow"""
    executions = await execution_service.get_flow_executions(flow_id, skip, limit)
    
    return ExecutionListResponse(
        items=executions,
        total=len(executions)  # In a real implementation, this would be a count query
    )

@router.get("/", response_model=ExecutionListResponse)
async def get_recent_executions(
    limit: int = Query(10, ge=1, le=50),
    execution_service: ExecutionService = Depends(get_execution_service)
):
    """Get recent executions across all flows"""
    executions = await execution_service.get_recent_executions(limit)
    
    return ExecutionListResponse(
        items=executions,
        total=len(executions)
    )

@router.get("/stats", response_model=Dict[str, Any])
async def get_execution_stats(
    execution_service: ExecutionService = Depends(get_execution_service)
):
    """Get execution statistics"""
    return await execution_service.get_execution_stats()
