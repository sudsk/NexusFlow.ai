# backend/tests/test_services.py
import os
import sys
import pytest
import asyncio
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.entities.flow import Flow
from backend.services.flow.flow_service import FlowService
from backend.services.execution.execution_service import ExecutionService
from backend.services.tool.tool_service import ToolService


class TestFlowService:
    @pytest.mark.asyncio
    async def test_create_flow(self):
        # Mock repository
        mock_flow_repo = MagicMock()
        mock_flow_repo.create.return_value = Flow(
            flow_id="test-flow-id",
            name="Test Flow",
            framework="langgraph",
            agents=[{
                "name": "Test Agent",
                "model_provider": "openai",
                "model_name": "gpt-4"
            }]
        )
        
        # Mock adapter registry
        mock_adapter_registry = MagicMock()
        mock_adapter = MagicMock()
        mock_adapter.get_framework_name.return_value = "langgraph"
        mock_adapter.get_supported_features.return_value = {
            "multi_agent": True,
            "tools": True
        }
        mock_adapter_registry.get_adapter.return_value = mock_adapter
        
        # Create service with mocks
        flow_service = FlowService(mock_flow_repo, mock_adapter_registry)
        
        # Test data
        flow_data = {
            "name": "Test Flow",
            "description": "Flow for testing",
            "framework": "langgraph",
            "agents": [
                {
                    "name": "Test Agent",
                    "model_provider": "openai",
                    "model_name": "gpt-4"
                }
            ],
            "max_steps": 10
        }
        
        # Call service method
        created_flow = await flow_service.create_flow(flow_data)
        
        # Verify
        assert created_flow is not None
        assert created_flow.name == "Test Flow"
        assert created_flow.framework == "langgraph"
        assert len(created_flow.agents) == 1
        assert mock_flow_repo.create.called
    
    @pytest.mark.asyncio
    async def test_validate_flow(self):
        # Mock repository
        mock_flow_repo = MagicMock()
        
        # Mock adapter registry
        mock_adapter_registry = MagicMock()
        mock_adapter = MagicMock()
        mock_adapter.validate_flow.return_value = {
            "valid": True,
            "errors": [],
            "warnings": ["Test warning"]
        }
        mock_adapter_registry.get_adapter.return_value = mock_adapter
        
        # Create service with mocks
        flow_service = FlowService(mock_flow_repo, mock_adapter_registry)
        
        # Test data
        flow_data = {
            "name": "Test Flow",
            "framework": "langgraph",
            "agents": [
                {
                    "name": "Test Agent",
                    "model_provider": "openai",
                    "model_name": "gpt-4"
                }
            ]
        }
        
        # Call service method
        validation_result = await flow_service.validate_flow(flow_data)
        
        # Verify
        assert validation_result is not None
        assert validation_result["valid"] is True
        assert len(validation_result["warnings"]) == 1
        assert mock_adapter.validate_flow.called


class TestExecutionService:
    @pytest.mark.asyncio
    async def test_execute_flow(self):
        # Mock repositories
        mock_flow_repo = MagicMock()
        mock_flow = Flow(
            flow_id="test-flow-id",
            name="Test Flow",
            framework="langgraph",
            agents=[{
                "name": "Test Agent",
                "model_provider": "openai",
                "model_name": "gpt-4"
            }]
        )
        mock_flow_repo.get_by_id.return_value = mock_flow
        
        mock_execution_repo = MagicMock()
        mock_execution_repo.create.return_value = MagicMock(id="test-execution-id")
        
        # Mock adapter registry
        mock_adapter_registry = MagicMock()
        mock_adapter = MagicMock()
        mock_adapter.convert_flow.return_value = {"type": "langgraph_flow"}
        mock_adapter.execute_flow.return_value = {
            "output": {"content": "Test result"},
            "execution_trace": [],
            "steps": 3
        }
        mock_adapter_registry.get_adapter.return_value = mock_adapter
        
        # Create service with mocks
        execution_service = ExecutionService(
            flow_repository=mock_flow_repo,
            execution_repository=mock_execution_repo
        )
        execution_service.adapter_registry = mock_adapter_registry
        
        # Test data
        flow_id = "test-flow-id"
        input_data = {"query": "test query"}
        
        # Call service method
        result = await execution_service.execute_flow(flow_id, input_data)
        
        # Verify
        assert result is not None
        assert "execution_id" in result
        assert mock_flow_repo.get_by_id.called
        assert mock_execution_repo.create.called
        assert mock_adapter.convert_flow.called
        assert mock_adapter.execute_flow.called


class TestToolService:
    @pytest.mark.asyncio
    async def test_get_all_tools(self):
        # Mock repository
        mock_tool_repo = MagicMock()
        mock_tool_repo.get_all.return_value = [
            MagicMock(
                id="tool-1",
                name="web_search",
                description="Search the web",
                parameters={"type": "object"},
                is_enabled=True,
                metadata={"compatible_frameworks": ["langgraph", "crewai"]}
            ),
            MagicMock(
                id="tool-2",
                name="data_analysis",
                description="Analyze data",
                parameters={"type": "object"},
                is_enabled=True,
                metadata={"compatible_frameworks": ["langgraph"]}
            )
        ]
        
        # Create service with mock
        tool_service = ToolService(mock_tool_repo)
        
        # Call service method
        tools = await tool_service.get_all_tools()
        
        # Verify
        assert tools is not None
        assert len(tools) == 2
        assert tools[0]["name"] == "web_search"
        assert tools[1]["name"] == "data_analysis"
        assert mock_tool_repo.get_all.called
        
        # Test with framework filter
        tools_langgraph = await tool_service.get_all_tools(framework="langgraph")
        assert len(tools_langgraph) == 2
        
        tools_crewai = await tool_service.get_all_tools(framework="crewai")
        assert len(tools_crewai) == 1
        assert tools_crewai[0]["name"] == "web_search"
    
    @pytest.mark.asyncio
    async def test_execute_tool(self):
        # Mock repository
        mock_tool_repo = MagicMock()
        mock_tool = MagicMock(
            name="web_search",
            description="Search the web",
            parameters={"type": "object"},
            is_enabled=True,
            function_name="web_search"
        )
        mock_tool_repo.get_by_name.return_value = mock_tool
        
        # Create service with mock
        tool_service = ToolService(mock_tool_repo)
        
        # Mock the _tool_cache with a function
        mock_function = MagicMock()
        mock_function.return_value = {"result": "Test search result"}
        tool_service._tool_cache = {"web_search": mock_function}
        
        # Test data
        tool_name = "web_search"
        params = {"query": "test query"}
        
        # Call service method
        with patch.object(tool_service, 'get_tool_function', return_value=mock_function):
            result = await tool_service.execute_tool(tool_name, params)
        
        # Verify
        assert result is not None
        assert "result" in result
        assert result["status"] == "success"
        assert mock_tool_repo.get_by_name.called
        assert mock_function.called
        mock_function.assert_called_with(params)
    
    @pytest.mark.asyncio
    async def test_get_available_tools_for_flow(self):
        # Mock repository
        mock_tool_repo = MagicMock()
        mock_tool_repo.get_all.return_value = [
            MagicMock(
                id="tool-1",
                name="web_search",
                description="Search the web",
                is_enabled=True,
                metadata={"compatible_frameworks": ["langgraph", "crewai"]}
            ),
            MagicMock(
                id="tool-2",
                name="data_analysis",
                description="Analyze data",
                is_enabled=True,
                metadata={"compatible_frameworks": ["langgraph"]}
            ),
            MagicMock(
                id="tool-3",
                name="disabled_tool",
                description="Disabled tool",
                is_enabled=False,
                metadata={"compatible_frameworks": ["langgraph", "crewai"]}
            )
        ]
        
        # Create service with mock
        tool_service = ToolService(mock_tool_repo)
        
        # Mock _convert_to_dict method
        def mock_convert(tool):
            if not tool:
                return None
            return {
                "id": tool.id,
                "name": tool.name,
                "description": tool.description,
                "is_enabled": tool.is_enabled,
                "metadata": tool.metadata
            }
        
        tool_service._convert_to_dict = mock_convert
        
        # Call service method
        langgraph_tools = await tool_service.get_available_tools_for_flow("langgraph")
        
        # Verify
        assert langgraph_tools is not None
        assert len(langgraph_tools) == 2  # Should exclude the disabled tool
        
        crewai_tools = await tool_service.get_available_tools_for_flow("crewai")
        assert len(crewai_tools) == 1  # Should only have web_search
        
        # Test with enabled_only=False
        all_langgraph_tools = await tool_service.get_available_tools_for_flow("langgraph", enabled_only=False)
        assert len(all_langgraph_tools) == 3  # Should include the disabled tool
