# backend/db/models/flow_model.py
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class FlowModel(Base):
    __tablename__ = "flows"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    executions = relationship("ExecutionModel", back_populates="flow", cascade="all, delete-orphan")
    deployments = relationship("DeploymentModel", back_populates="flow", cascade="all, delete-orphan")

class ExecutionModel(Base):
    __tablename__ = "executions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    flow_id = Column(String(36), ForeignKey("flows.id"))
    framework = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    input = Column(JSON)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    execution_trace = Column(JSON, nullable=True)
    
    flow = relationship("FlowModel", back_populates="executions")
