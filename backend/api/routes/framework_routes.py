# backend/api/routes/framework_routes.py
from fastapi import APIRouter, Depends
from typing import Dict, Any
from sqlalchemy.orm import Session

from ...db.session import get_db
from ...services.flow.flow_service import FlowService
from ...db.repositories.flow_repository import FlowRepository

router = APIRouter(prefix="/frameworks", tags=["frameworks"])

def get_flow_service(db: Session = Depends(get_db)):
    flow_repo = FlowRepository(db)
    return FlowService(flow_repo)

@router.get("/", response_model=Dict[str, Dict[str, bool]])
async def get_frameworks(
    flow_service: FlowService = Depends(get_flow_service)
):
    """Get information about available frameworks"""
    return await flow_service.get_frameworks()
