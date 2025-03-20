# backend/db/models/tool_model.py
from sqlalchemy import Column, String, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

from .base import Base

class ToolModel(Base):
    __tablename__ = "tools"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    parameters = Column(JSON, nullable=False)
    function_name = Column(String(100))
    is_enabled = Column(Boolean, default=True)
    requires_authentication = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    metadata = Column(JSON)
