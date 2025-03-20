# backend/tests/test_repositories.py
import os
import sys
import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Add parent directory to path so we can import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.models.base import Base
from backend.db.models.flow_model import FlowModel, ExecutionModel
from backend.db.models.tool_model import ToolModel
from backend.db.repositories.flow_repository import FlowRepository
from backend.db.repositories.tool_repository import ToolRepository
from backend.db.repositories.execution_repository import ExecutionRepository


# Setup test database
@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Use SQLite in-memory database for tests
    engine = create_engine("sqlite:///:memory:", poolclass=NullPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


class TestFlowRepository:
    def test_create_flow(self, db_session):
        repo = FlowRepository(db_session)
        
        # Create test flow data
        flow_data = {
            "name": "Test Flow",
            "description": "Flow for testing",
            "framework": "langgraph",
            "config": {
                "agents": [
                    {
                        "name": "Test Agent",
                        "model_provider": "openai",
                        "model_name": "gpt-4"
                    }
                ],
                "max_steps": 10
            }
        }
        
        # Create flow model
        flow_model = FlowModel(**flow_data)
        db_session.add(flow_model)
        db_session.commit()
        db_session.refresh(flow_model)
        
        # Test retrieval
        retrieved_flow = repo.get_by_id(flow_model.id)
        assert retrieved_flow is not None
        assert retrieved_flow.name == "Test Flow"
        assert retrieved_flow.framework == "langgraph"
    
    def test_update_flow(self, db_session):
        repo = FlowRepository(db_session)
        
        # Create test flow data
        flow_data = {
            "name": "Original Flow",
            "description": "Flow for testing",
            "framework": "langgraph",
            "config": {
                "agents": [
                    {
                        "name": "Test Agent",
                        "model_provider": "openai",
                        "model_name": "gpt-4"
                    }
                ],
                "max_steps": 10
            }
        }
        
        # Create flow model
        flow_model = FlowModel(**flow_data)
        db_session.add(flow_model)
        db_session.commit()
        db_session.refresh(flow_model)
        
        # Update flow
        flow_id = flow_model.id
        
        # Update the flow
        update_result = repo.update(flow_id, {"name": "Updated Flow", "description": "Updated description"})
        assert update_result is not None
        
        # Verify update
        updated_flow = repo.get_by_id(flow_id)
        assert updated_flow.name == "Updated Flow"
        assert updated_flow.description == "Updated description"
    
    def test_delete_flow(self, db_session):
        repo = FlowRepository(db_session)
        
        # Create test flow data
        flow_data = {
            "name": "Flow to Delete",
            "framework": "langgraph",
            "config": {}
        }
        
        # Create flow model
        flow_model = FlowModel(**flow_data)
        db_session.add(flow_model)
        db_session.commit()
        db_session.refresh(flow_model)
        
        flow_id = flow_model.id
        
        # Verify it exists
        assert repo.get_by_id(flow_id) is not None
        
        # Delete it
        delete_result = repo.delete(flow_id)
        assert delete_result is True
        
        # Verify it's gone
        assert repo.get_by_id(flow_id) is None


class TestToolRepository:
    def test_create_tool(self, db_session):
        repo = ToolRepository(db_session)
        
        # Create test tool data
        tool_data = {
            "name": "web_search",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            },
            "function_name": "search_web",
            "is_enabled": True,
            "requires_authentication": False,
            "metadata": {
                "category": "utility",
                "compatible_frameworks": ["langgraph", "crewai"]
            }
        }
        
        # Create tool model
        tool_model = ToolModel(**tool_data)
        db_session.add(tool_model)
        db_session.commit()
        db_session.refresh(tool_model)
        
        # Test retrieval
        retrieved_tool = repo.get_by_id(tool_model.id)
        assert retrieved_tool is not None
        assert retrieved_tool.name == "web_search"
        assert retrieved_tool.function_name == "search_web"
        
        # Test retrieval by name
        retrieved_by_name = repo.get_by_name("web_search")
        assert retrieved_by_name is not None
        assert retrieved_by_name.id == tool_model.id
    
    def test_update_tool(self, db_session):
        repo = ToolRepository(db_session)
        
        # Create test tool data
        tool_data = {
            "name": "original_tool",
            "description": "Original description",
            "parameters": {},
            "is_enabled": True
        }
        
        # Create tool model
        tool_model = ToolModel(**tool_data)
        db_session.add(tool_model)
        db_session.commit()
        db_session.refresh(tool_model)
        
        tool_id = tool_model.id
        
        # Update the tool
        update_result = repo.update(tool_id, {
            "name": "updated_tool", 
            "description": "Updated description"
        })
        assert update_result is not None
        
        # Verify update
        updated_tool = repo.get_by_id(tool_id)
        assert updated_tool.name == "updated_tool"
        assert updated_tool.description == "Updated description"
        
        # Verify the old name doesn't work anymore
        assert repo.get_by_name("original_tool") is None
        
        # Verify the new name works
        assert repo.get_by_name("updated_tool") is not None


class TestExecutionRepository:
    def test_create_execution(self, db_session):
        # First create a flow
        flow_data = {
            "name": "Test Flow",
            "framework": "langgraph",
            "config": {}
        }
        flow_model = FlowModel(**flow_data)
        db_session.add(flow_model)
        db_session.commit()
        db_session.refresh(flow_model)
        
        # Now create an execution
        repo = ExecutionRepository(db_session)
        execution_data = {
            "flow_id": flow_model.id,
            "framework": "langgraph",
            "status": "completed",
            "started_at": datetime.datetime.utcnow(),
            "completed_at": datetime.datetime.utcnow(),
            "input": {"query": "test query"},
            "result": {"output": "test result"},
            "execution_trace": [{"step": 1, "agent": "agent1", "output": "test output"}]
        }
        
        # Create execution model
        execution_model = ExecutionModel(**execution_data)
        db_session.add(execution_model)
        db_session.commit()
        db_session.refresh(execution_model)
        
        # Test retrieval
        retrieved_execution = repo.get_by_id(execution_model.id)
        assert retrieved_execution is not None
        assert retrieved_execution.flow_id == flow_model.id
        assert retrieved_execution.status == "completed"
    
    def test_get_by_flow_id(self, db_session):
        # First create a flow
        flow_data = {
            "name": "Test Flow",
            "framework": "langgraph",
            "config": {}
        }
        flow_model = FlowModel(**flow_data)
        db_session.add(flow_model)
        db_session.commit()
        db_session.refresh(flow_model)
        
        # Create multiple executions for the flow
        repo = ExecutionRepository(db_session)
        
        for i in range(3):
            execution_data = {
                "flow_id": flow_model.id,
                "framework": "langgraph",
                "status": "completed",
                "started_at": datetime.datetime.utcnow(),
                "input": {"query": f"test query {i}"}
            }
            execution_model = ExecutionModel(**execution_data)
            db_session.add(execution_model)
        
        db_session.commit()
        
        # Test retrieval by flow_id
        executions = repo.get_by_flow_id(flow_model.id)
        assert len(executions) == 3
        
        # Test with status filter
        completed_executions = repo.get_by_flow_id(flow_model.id, status="completed")
        assert len(completed_executions) == 3
        
        failed_executions = repo.get_by_flow_id(flow_model.id, status="failed")
        assert len(failed_executions) == 0
    
    def test_get_stats(self, db_session):
        # First create a flow
        flow_data = {
            "name": "Test Flow",
            "framework": "langgraph",
            "config": {}
        }
        flow_model = FlowModel(**flow_data)
        db_session.add(flow_model)
        db_session.commit()
        db_session.refresh(flow_model)
        
        # Create executions with different statuses
        repo = ExecutionRepository(db_session)
        
        # Completed executions
        for i in range(5):
            execution_data = {
                "flow_id": flow_model.id,
                "framework": "langgraph",
                "status": "completed",
                "started_at": datetime.datetime.utcnow(),
                "completed_at": datetime.datetime.utcnow(),
                "input": {"query": f"completed query {i}"}
            }
            execution_model = ExecutionModel(**execution_data)
            db_session.add(execution_model)
        
        # Failed executions
        for i in range(2):
            execution_data = {
                "flow_id": flow_model.id,
                "framework": "langgraph",
                "status": "failed",
                "started_at": datetime.datetime.utcnow(),
                "completed_at": datetime.datetime.utcnow(),
                "input": {"query": f"failed query {i}"},
                "error": "Test error"
            }
            execution_model = ExecutionModel(**execution_data)
            db_session.add(execution_model)
        
        # Running executions
        for i in range(1):
            execution_data = {
                "flow_id": flow_model.id,
                "framework": "langgraph",
                "status": "running",
                "started_at": datetime.datetime.utcnow(),
                "input": {"query": f"running query {i}"}
            }
            execution_model = ExecutionModel(**execution_data)
            db_session.add(execution_model)
        
        db_session.commit()
        
        # Test stats
        stats = repo.get_stats()
        assert stats["total_executions"] == 8
        assert stats["completed_executions"] == 5
        assert stats["failed_executions"] == 2
        
        # Test with more specific stats
        success_rate = stats["success_rate"]
        assert success_rate == 71.43  # 5/7 completed, excluding running
