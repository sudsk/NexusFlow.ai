# backend/tests/test_services.py
import os
import sys
import pytest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add parent directory to path so we can import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.entities.flow import Flow
from backend.services.flow.flow_service import FlowService
from backend.services.execution.execution_service import ExecutionService
from backend.services.tool.tool_service import ToolService
from backend.services.deployment.deployment_service import DeploymentService


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
        flow_service = FlowService(mock_flow_repo)
        flow_service.adapter_registry = mock_adapter_registry
        
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
        flow_service = FlowService(mock_flow_repo)
        flow_service.adapter_registry = mock_adapter_registry
        
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
        assert mock_adapter_registry.get_adapter.called
        assert mock_adapter.validate_flow.called

    @pytest.mark.asyncio
    async def test_update_flow(self):
        # Mock repository
        mock_flow_repo = MagicMock()
        mock_flow_repo.get_by_id.return_value = Flow(
            flow_id="test-flow-id",
            name="Original Flow",
            framework="langgraph",
            agents=[{
                "name": "Test Agent",
                "model_provider": "openai",
                "model_name": "gpt-4"
            }]
        )
        mock_flow_repo.update.return_value = Flow(
            flow_id="test-flow-id",
            name="Updated Flow",
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
        mock_adapter_registry.get_adapter.return_value = mock_adapter
        
        # Create service with mocks
        flow_service = FlowService(mock_flow_repo)
        flow_service.adapter_registry = mock_adapter_registry
        
        # Call service method
        updated_flow = await flow_service.update_flow("test-flow-id", {"name": "Updated Flow"})
        
        # Verify
        assert updated_flow is not None
        assert updated_flow.name == "Updated Flow"
        assert mock_flow_repo.get_by_id.called
        assert mock_flow_repo.update.called

    @pytest.mark.asyncio
    async def test_delete_flow(self):
        # Mock repository
        mock_flow_repo = MagicMock()
        mock_flow_repo.delete.return_value = True
        
        # Mock adapter registry
        mock_adapter_registry = MagicMock()
        
        # Create service with mocks
        flow_service = FlowService(mock_flow_repo)
        flow_service.adapter_registry = mock_adapter_registry
        
        # Call service method
        result = await flow_service.delete_flow("test-flow-id")
        
        # Verify
        assert result is True
        assert mock_flow_repo.delete.called
        mock_flow_repo.delete.assert_called_with("test-flow-id")

    @pytest.mark.asyncio
    async def test_export_flow(self):
        # Mock repository
        mock_flow_repo = MagicMock()
        mock_flow_repo.get_by_id.return_value = Flow(
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
        mock_adapter.convert_flow.return_value = {"converted": "flow-data"}
        mock_adapter_registry.get_adapter.return_value = mock_adapter
        
        # Create service with mocks
        flow_service = FlowService(mock_flow_repo)
        flow_service.adapter_registry = mock_adapter_registry
        
        # Call service method
        result = await flow_service.export_flow("test-flow-id", "crewai")
        
        # Verify
        assert result is not None
        assert result["flow_id"] == "test-flow-id"
        assert result["target_framework"] == "crewai"
        assert "exported_config" in result
        assert mock_flow_repo.get_by_id.called
        assert mock_adapter_registry.get_adapter.called
        assert mock_adapter.convert_flow.called


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
        mock_execution = MagicMock(
            id="test-execution-id",
            flow_id="test-flow-id",
            framework="langgraph",
            status="pending",
            started_at=datetime.utcnow()
        )
        mock_execution_repo.create.return_value = mock_execution
        
        # Mock adapter registry
        mock_adapter_registry = MagicMock()
        mock_adapter = MagicMock()
        mock_adapter.convert_flow.return_value = {"type": "langgraph_flow"}
        mock_adapter.execute_flow.return_value = {
            "output": {"content": "Test result"},
            "execution_trace": [{"step": 1, "type": "agent_execution"}],
            "steps": 1
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
        assert result["status"] == "completed"
        assert "result" in result
        assert mock_flow_repo.get_by_id.called
        assert mock_execution_repo.create.called
        assert mock_execution_repo.update.called
        assert mock_adapter.convert_flow.called
        assert mock_adapter.execute_flow.called

    @pytest.mark.asyncio
    async def test_get_execution_status(self):
        # Mock repository
        mock_flow_repo = MagicMock()
        mock_execution_repo = MagicMock()
        mock_execution = MagicMock(
            id="test-execution-id",
            flow_id="test-flow-id",
            framework="langgraph",
            status="completed",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            result={"output": {"content": "Test result"}},
            execution_trace=[{"step": 1, "type": "agent_execution"}]
        )
        mock_execution_repo.get_by_id.return_value = mock_execution
        
        # Create service with mocks
        execution_service = ExecutionService(
            flow_repository=mock_flow_repo,
            execution_repository=mock_execution_repo
        )
        
        # Call service method
        result = await execution_service.get_execution_status("test-execution-id")
        
        # Verify
        assert result is not None
        assert result["id"] == "test-execution-id"
        assert result["status"] == "completed"
        assert "result" in result
        assert "execution_trace" in result
        assert mock_execution_repo.get_by_id.called
        mock_execution_repo.get_by_id.assert_called_with("test-execution-id")

    @pytest.mark.asyncio
    async def test_get_flow_executions(self):
        # Mock repository
        mock_flow_repo = MagicMock()
        mock_execution_repo = MagicMock()
        mock_executions = [
            MagicMock(
                id=f"execution-{i}",
                flow_id="test-flow-id",
                status="completed",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            ) for i in range(3)
        ]
        mock_execution_repo.get_by_flow_id.return_value = mock_executions
        
        # Create service with mocks
        execution_service = ExecutionService(
            flow_repository=mock_flow_repo,
            execution_repository=mock_execution_repo
        )
        
        # Call service method
        results = await execution_service.get_flow_executions("test-flow-id")
        
        # Verify
        assert results is not None
        assert len(results) == 3
        assert mock_execution_repo.get_by_flow_id.called
        mock_execution_repo.get_by_flow_id.assert_called_with("test-flow-id", 0, 100, None)


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
                metadata={"compatible_frameworks": ["langgraph", "crewai", "autogen"]}
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
        
        # Add mock for convert_to_dict method
        tool_service._convert_to_dict = lambda tool: {
            "id": tool.id,
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
            "is_enabled": tool.is_enabled,
            "metadata": tool.metadata
        }
        
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


class TestDeploymentService:
    @pytest.mark.asyncio
    async def test_deploy_flow(self):
        # Mock repositories
        mock_flow_repo = MagicMock()
        mock_flow_repo.get_by_id.return_value = Flow(
            flow_id="test-flow-id",
            name="Test Flow",
            framework="langgraph",
            agents=[{
                "name": "Test Agent",
                "model_provider": "openai",
                "model_name": "gpt-4"
            }]
        )
        
        mock_deployment_repo = MagicMock()
        mock_deployment = MagicMock(
            id="test-deployment-id",
            flow_id="test-flow-id",
            name="Test Deployment",
            version="v1",
            status="active",
            api_key="test-api-key",
            endpoint_url="https://api.nexusflow.ai/flows/test-deployment-id/execute",
            settings={}
        )
        mock_deployment_repo.create.return_value = mock_deployment
        
        # Create service with mocks
        deployment_service = DeploymentService(
            flow_repository=mock_flow_repo,
            deployment_repository=mock_deployment_repo
        )
        
        # Test data
        flow_id = "test-flow-id"
        deployment_data = {
            "name": "Test Deployment",
            "version": "v1",
            "settings": {}
        }
        
        # Call service method
        result = await deployment_service.deploy_flow(flow_id, deployment_data)
        
        # Verify
        assert result is not None
        assert result["flow_id"] == flow_id
        assert result["name"] == "Test Deployment"
        assert result["version"] == "v1"
        assert result["status"] == "active"
        assert "endpoint_url" in result
        assert mock_flow_repo.get_by_id.called
        assert mock_deployment_repo.create.called

    @pytest.mark.asyncio
    async def test_get_flow_deployments(self):
        # Mock repositories
        mock_flow_repo = MagicMock()
        mock_deployment_repo = MagicMock()
        mock_deployments = [
            MagicMock(
                id=f"deployment-{i}",
                flow_id="test-flow-id",
                name=f"Test Deployment {i}",
                version="v1",
                status="active",
                endpoint_url=f"https://api.nexusflow.ai/flows/deployment-{i}/execute"
            ) for i in range(2)
        ]
        mock_deployment_repo.get_by_flow_id.return_value = mock_deployments
        
        # Create service with mocks
        deployment_service = DeploymentService(
            flow_repository=mock_flow_repo,
            deployment_repository=mock_deployment_repo
        )
        
        # Override _convert_to_dict to handle mock objects
        def mock_convert(deployment):
            return {
                "id": deployment.id,
                "flow_id": deployment.flow_id,
                "name": deployment.name,
                "version": deployment.version,
                "status": deployment.status,
                "endpoint_url": deployment.endpoint_url,
                "created_at": deployment.created_at.isoformat() if hasattr(deployment, 'created_at') and deployment.created_at else None,
                "updated_at": deployment.updated_at.isoformat() if hasattr(deployment, 'updated_at') and deployment.updated_at else None,
                "settings": deployment.settings or {}
            }
        
        deployment_service._convert_to_dict = mock_convert
        
        # Call service method
        results = await deployment_service.get_flow_deployments("test-flow-id")
        
        # Verify
        assert results is not None
        assert len(results) == 2
        assert results[0]["flow_id"] == "test-flow-id"
        assert mock_deployment_repo.get_by_flow_id.called
        mock_deployment_repo.get_by_flow_id.assert_called_with("test-flow-id")
