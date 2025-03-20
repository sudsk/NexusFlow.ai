# backend/tests/integration/test_flow_execution.py
import os
import sys
import json
import pytest
import asyncio
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.core.entities.flow import Flow
from backend.adapters.registry import get_adapter_registry
from backend.adapters.langgraph.langgraph_adapter import LangGraphAdapter
from backend.services.execution.execution_service import ExecutionService
from backend.services.flow.flow_service import FlowService
from backend.services.tool.tool_service import ToolService
from backend.services.flow.validator_service import get_flow_validator

# Test data
TEST_FLOW = {
    "name": "Test Research Flow",
    "description": "A test flow for integration testing",
    "framework": "langgraph",
    "agents": [
        {
            "agent_id": "researcher",
            "name": "Researcher",
            "model_provider": "openai",
            "model_name": "gpt-4",
            "system_message": "You are a research agent that searches for information.",
            "tool_names": ["web_search"]
        },
        {
            "agent_id": "analyst",
            "name": "Analyst",
            "model_provider": "anthropic",
            "model_name": "claude-3-opus",
            "system_message": "You are an analysis agent that processes information.",
            "tool_names": ["data_analysis"]
        }
    ],
    "tools": {
        "web_search": {
            "description": "Search the web for information",
            "config": {"use_async": True}
        },
        "data_analysis": {
            "description": "Analyze data and generate insights",
            "config": {"streaming": True}
        }
    },
    "max_steps": 10
}

TEST_INPUT = {
    "query": "What are the latest developments in AI?"
}

# Mock responses
MOCK_EXECUTION_RESULT = {
    "execution_id": "test-execution-id",
    "flow_id": "test-flow-id",
    "status": "completed",
    "result": {
        "output": {
            "content": "The latest developments in AI include advancements in multimodal models, more efficient training techniques, and applications in scientific research."
        }
    },
    "execution_trace": [
        {
            "step": 1,
            "agent_id": "researcher",
            "agent_name": "Researcher",
            "type": "agent_execution",
            "input": {"query": "What are the latest developments in AI?"},
            "output": {
                "content": "I'll search for the latest developments in AI."
            }
        },
        {
            "step": 2,
            "agent_id": "researcher",
            "agent_name": "Researcher",
            "type": "tool_execution",
            "input": {"query": "latest developments in artificial intelligence"},
            "output": {
                "content": "Search results about AI developments"
            }
        },
        {
            "step": 3,
            "agent_id": "researcher",
            "agent_name": "Researcher",
            "type": "delegation",
            "decision": {
                "action": "delegate",
                "target": "analyst",
                "reasoning": "Need to analyze the search results"
            }
        },
        {
            "step": 4,
            "agent_id": "analyst",
            "agent_name": "Analyst",
            "type": "agent_execution",
            "input": {"search_results": "Search results about AI developments"},
            "output": {
                "content": "Based on the search results, I'll analyze the key trends in AI development."
            }
        },
        {
            "step": 5,
            "agent_id": "analyst",
            "agent_name": "Analyst",
            "type": "complete",
            "output": {
                "content": "The latest developments in AI include advancements in multimodal models, more efficient training techniques, and applications in scientific research."
            }
        }
    ]
}

@pytest.mark.asyncio
async def test_flow_validation():
    """Test flow validation functionality"""
    
    # Get flow validator
    validator = get_flow_validator()
    
    # Validate test flow
    validation_result = validator.validate_flow(TEST_FLOW)
    
    # Check validation result
    assert validation_result["valid"] == True, f"Flow validation failed: {validation_result['errors']}"
    
    # Test invalid flow (no agents)
    invalid_flow = {
        "name": "Invalid Flow",
        "framework": "langgraph",
        "agents": []
    }
    
    invalid_result = validator.validate_flow(invalid_flow)
    assert invalid_result["valid"] == False
    assert len(invalid_result["errors"]) > 0
    assert any("at least one agent" in error for error in invalid_result["errors"])

@pytest.mark.asyncio
async def test_adapter_conversion():
    """Test adapter flow conversion"""
    
    # Get adapter registry
    registry = get_adapter_registry()
    
    # Get LangGraph adapter
    try:
        adapter = registry.get_adapter("langgraph")
    except ValueError:
        # Skip test if LangGraph adapter not available
        pytest.skip("LangGraph adapter not available")
    
    # Convert flow
    converted_flow = adapter.convert_flow(TEST_FLOW)
    
    # Check conversion result
    assert converted_flow is not None
    assert "agents" in converted_flow
    assert len(converted_flow["agents"]) == 2
    assert "tools" in converted_flow
    assert "web_search" in converted_flow["tools"]
    assert "data_analysis" in converted_flow["tools"]

@pytest.mark.asyncio
async def test_flow_execution_service():
    """Test execution service with mocked adapter"""
    
    # Create mock for flow repository
    mock_flow_repo = MagicMock()
    mock_flow_repo.get_by_id.return_value = Flow.from_dict({
        "flow_id": "test-flow-id",
        **TEST_FLOW
    })
    
    # Create mock for execution repository
    mock_execution_repo = MagicMock()
    mock_execution = MagicMock(
        id="test-execution-id",
        flow_id="test-flow-id",
        framework="langgraph",
        status="pending",
        started_at="2024-03-10T10:00:00Z",
        input=TEST_INPUT
    )
    mock_execution_repo.create.return_value = mock_execution
    
    # Create mock adapter
    mock_adapter = MagicMock()
    mock_adapter.convert_flow.return_value = {"type": "langgraph_flow"}
    mock_adapter.execute_flow.return_value = MOCK_EXECUTION_RESULT
    
    # Create mock adapter registry
    mock_adapter_registry = MagicMock()
    mock_adapter_registry.get_adapter.return_value = mock_adapter
    
    # Create execution service with mocks
    execution_service = ExecutionService(
        flow_repository=mock_flow_repo,
        execution_repository=mock_execution_repo
    )
    execution_service.adapter_registry = mock_adapter_registry
    
    # Execute flow
    result = await execution_service.execute_flow(
        flow_id="test-flow-id",
        input_data=TEST_INPUT,
        framework="langgraph"
    )
    
    # Check execution result
    assert result is not None
    assert "execution_id" in result
    assert mock_flow_repo.get_by_id.called
    assert mock_execution_repo.create.called
    assert mock_adapter.convert_flow.called
    assert mock_adapter.execute_flow.called

@pytest.mark.asyncio
async def test_tool_execution():
    """Test tool execution functionality"""
    
    # Create mocked tool repository
    mock_tool_repo = MagicMock()
    mock_tool_repo.get_by_name.return_value = MagicMock(
        name="web_search",
        description="Search the web for information",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        },
        is_enabled=True,
        function_name="web_search"
    )
    
    # Create tool service with mock
    tool_service = ToolService(mock_tool_repo)
    
    # Mock the web_search function
    async def mock_web_search(params, context=None):
        return {
            "results": [
                {
                    "title": f"Result for {params['query']}",
                    "link": "https://example.com/1",
                    "snippet": f"This is a mock search result for {params['query']}."
                }
            ],
            "query": params["query"]
        }
    
    # Add mock function to tool service
    tool_service._tool_cache = {"web_search": mock_web_search}
    
    # Test execute tool
    with patch.object(tool_service, 'get_tool_function', return_value=mock_web_search):
        result = await tool_service.execute_tool(
            tool_name="web_search",
            params={"query": "test query"},
            context={"execution_id": "test-execution-id"}
        )
    
    # Check tool execution result
    assert result is not None
    assert "status" in result
    assert result["status"] == "success"
    assert "result" in result
    assert "results" in result["result"]
    assert len(result["result"]["results"]) > 0

@pytest.mark.asyncio
async def test_end_to_end_execution_mock():
    """Test end-to-end flow execution with mocked components"""
    
    # Skip on CI/CD environments
    if os.environ.get("CI"):
        pytest.skip("Skipping end-to-end test in CI environment")
    
    # Create a simple flow with one agent
    test_flow = {
        "name": "Simple Test Flow",
        "description": "A simple test flow for end-to-end testing",
        "framework": "langgraph",
        "agents": [
            {
                "agent_id": "simple_agent",
                "name": "Simple Agent",
                "model_provider": "openai",
                "model_name": "gpt-3.5-turbo",
                "system_message": "You are a simple test agent.",
                "tool_names": []
            }
        ],
        "max_steps": 3
    }
    
    flow_entity = Flow.from_dict({
        "flow_id": "test-simple-flow",
        **test_flow
    })
    
    # Create mock repositories
    mock_flow_repo = MagicMock()
    mock_flow_repo.get_by_id.return_value = flow_entity
    
    mock_execution_repo = MagicMock()
    mock_execution = MagicMock(
        id="test-simple-execution",
        flow_id="test-simple-flow",
        framework="langgraph",
        status="pending",
        started_at="2024-03-10T10:00:00Z",
        input={"query": "Simple test query"}
    )
    mock_execution_repo.create.return_value = mock_execution
    
    # Create mock LangGraph adapter with simplified implementation
    class MockLangGraphAdapter(LangGraphAdapter):
        async def execute_flow(self, flow, input_data, step_callback=None):
            # Very simple mock implementation that returns a basic result
            await asyncio.sleep(0.1)  # Simulate some processing time
            
            # Create a simple execution trace
            trace = [
                {
                    "step": 1,
                    "agent_id": "simple_agent",
                    "agent_name": "Simple Agent",
                    "type": "agent_execution",
                    "input": input_data,
                    "output": {
                        "content": f"Processing query: {input_data.get('query')}",
                        "metadata": {"model": "openai/gpt-3.5-turbo"}
                    }
                },
                {
                    "step": 2,
                    "agent_id": "simple_agent",
                    "agent_name": "Simple Agent", 
                    "type": "agent_execution",
                    "output": {
                        "content": f"Result for query: {input_data.get('query')}",
                        "metadata": {"model": "openai/gpt-3.5-turbo"}
                    }
                },
                {
                    "step": 3,
                    "type": "complete"
                }
            ]
            
            # Call step callback if provided
            if step_callback:
                for step in trace:
                    await step_callback(step)
            
            return {
                "output": {
                    "content": f"Result for query: {input_data.get('query')}",
                    "metadata": {"framework": "langgraph", "iterations": 2}
                },
                "execution_trace": trace,
                "steps": len(trace)
            }
    
    # Create mock adapter registry
    mock_adapter_registry = MagicMock()
    mock_adapter = MockLangGraphAdapter()
    mock_adapter_registry.get_adapter.return_value = mock_adapter
    
    # Create execution service with mocks
    execution_service = ExecutionService(
        flow_repository=mock_flow_repo,
        execution_repository=mock_execution_repo
    )
    execution_service.adapter_registry = mock_adapter_registry
    
    # Execute flow
    input_data = {"query": "Simple test query"}
    result = await execution_service.execute_flow(
        flow_id="test-simple-flow",
        input_data=input_data,
        streaming=False  # Don't run in background for test
    )
    
    # Check execution result
    assert result is not None
    assert "execution_id" in result
    assert "result" in result
    assert "output" in result["result"]
    assert "content" in result["result"]["output"]
    assert input_data["query"] in result["result"]["output"]["content"]
    
    # Ensure execution repository was updated
    assert mock_execution_repo.update.called
    
    # Check that flow was properly converted
    assert mock_adapter.convert_flow.called

@pytest.mark.asyncio
async def test_flow_export():
    """Test flow export functionality"""
    
    # Create mock flow repository
    mock_flow_repo = MagicMock()
    mock_flow_repo.get_by_id.return_value = Flow.from_dict({
        "flow_id": "test-flow-id",
        **TEST_FLOW
    })
    
    # Create flow service with mock
    flow_service = FlowService(mock_flow_repo)
    
    # Create mock adapter registry with adapters for both frameworks
    mock_adapter_registry = MagicMock()
    
    # Create mock LangGraph adapter
    mock_langgraph_adapter = MagicMock()
    mock_langgraph_adapter.get_framework_name.return_value = "langgraph"
    mock_langgraph_adapter.convert_flow.return_value = {"type": "langgraph_flow"}
    
    # Create mock CrewAI adapter
    mock_crewai_adapter = MagicMock()
    mock_crewai_adapter.get_framework_name.return_value = "crewai"
    mock_crewai_adapter.convert_flow.return_value = {"type": "crewai_flow"}
    
    # Configure adapter registry to return mock adapters
    mock_adapter_registry.get_adapter.side_effect = lambda framework: (
        mock_langgraph_adapter if framework == "langgraph" else 
        mock_crewai_adapter if framework == "crewai" else
        None
    )
    
    # Set mock adapter registry
    flow_service.adapter_registry = mock_adapter_registry
    
    # Test export to CrewAI
    export_result = await flow_service.export_flow("test-flow-id", "crewai")
    
    # Check export result
    assert export_result is not None
    assert export_result["flow_id"] == "test-flow-id"
    assert export_result["original_framework"] == "langgraph"
    assert export_result["target_framework"] == "crewai"
    assert export_result["exported_config"]["type"] == "crewai_flow"
    
    # Verify adapters were called correctly
    mock_adapter_registry.get_adapter.assert_called_with("crewai")
    mock_crewai_adapter.convert_flow.assert_called_once()

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
