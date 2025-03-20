# backend/db/models/flow_model.py (updated)
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .base import Base

class FlowModel(Base):
    __tablename__ = "flows"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    framework = Column(String(50), default="langgraph")
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    executions = relationship("ExecutionModel", back_populates="flow", cascade="all, delete-orphan")
    deployments = relationship("DeploymentModel", back_populates="flow", cascade="all, delete-orphan")
