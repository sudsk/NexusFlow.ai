# backend/db/models/deployment_model.py
from sqlalchemy import Column, String, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .base import Base

class DeploymentModel(Base):
    __tablename__ = "deployments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    flow_id = Column(String(36), ForeignKey("flows.id"), nullable=False)
    name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    status = Column(String(20), default="active")
    api_key = Column(String(100), nullable=False)
    endpoint_url = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    settings = Column(JSON)
    
    # Relationships
    flow = relationship("FlowModel", back_populates="deployments")
