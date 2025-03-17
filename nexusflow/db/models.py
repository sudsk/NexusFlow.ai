from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from datetime import datetime
import uuid

Base = declarative_base()

class Flow(Base):
    __tablename__ = "flows"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    config = Column(JSON, nullable=False)
    
    executions = relationship("Execution", back_populates="flow", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="flow", cascade="all, delete-orphan")


class Execution(Base):
    __tablename__ = "executions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    flow_id = Column(String(36), ForeignKey("flows.id"))
    deployment_id = Column(String(36), ForeignKey("deployments.id"), nullable=True)
    status = Column(String(50), default="pending")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    input = Column(JSON)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    execution_trace = Column(JSON, nullable=True)
    
    flow = relationship("Flow", back_populates="executions")
    deployment = relationship("Deployment", back_populates="executions")


class Deployment(Base):
    __tablename__ = "deployments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    flow_id = Column(String(36), ForeignKey("flows.id"))
    version = Column(String(50), default="v1")
    description = Column(Text, nullable=True)
    api_key = Column(String(255), nullable=False)
    endpoint_url = Column(String(255), nullable=False)
    status = Column(String(50), default="active")
    deployed_at = Column(DateTime, default=datetime.utcnow)
    
    flow = relationship("Flow", back_populates="deployments")
    executions = relationship("Execution", back_populates="deployment")
    webhooks = relationship("Webhook", back_populates="deployment", cascade="all, delete-orphan")


class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    deployment_id = Column(String(36), ForeignKey("deployments.id"))
    url = Column(String(255), nullable=False)
    events = Column(JSON, default=lambda: ["completed", "failed"])
    secret = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    deployment = relationship("Deployment", back_populates="webhooks")


class CapabilityMetadata(Base):
    __tablename__ = "capability_metadata"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    capability_type = Column(String(100), nullable=False)
    agent_id = Column(String(36), nullable=False)
    score = Column(Float, default=1.0)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('capability_type', 'agent_id', name='uq_capability_agent'),
    )


class ToolExecution(Base):
    __tablename__ = "tool_executions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String(36), ForeignKey("executions.id"))
    tool_name = Column(String(100), nullable=False)
    parameters = Column(JSON)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Float, nullable=True)
    
    execution = relationship("Execution")
