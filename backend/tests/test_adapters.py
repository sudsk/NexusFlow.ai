# backend/tests/test_adapters.py
import os
import sys
import pytest
import asyncio
from unittest.mock import MagicMock, patch

# Add parent directory to path so we can import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.adapters.interfaces.base_adapter import FrameworkAdapter
from backend.adapters.langgraph.langgraph_adapter import LangGraphAdapter
from backend.adapters.crewai.crewai_adapter import CrewAIAdapter
from backend.adapters.registry import AdapterRegistry, get_adapter_registry


class TestAdapterRegistry:
    def test_registry_initialization(self):
        registry = AdapterRegistry()
        
        # Check default adapters are registered
        adapters = registry.get_all_adapters()
        assert "langgraph" in adapters
        assert "crewai" in adapters
        
        # Check adapter retrieval
        langgraph_adapter = registry.get_adapter("langgraph")
        assert isinstance(langgraph_adapter, LangGraphAdapter)
        
        crewai_adapter = registry.get_adapter("crewai")
        assert isinstance(crewai_adapter, CrewAIAdapter)
    
    def test_register_custom_adapter(self):
        registry = AdapterRegistry()
        
        # Create a mock adapter
        mock_adapter = MagicMock(spec=FrameworkAdapter)
        mock_adapter.get_framework_name.return_value = "mock_framework"
        mock_adapter.get_supported_features.return_value = {
            "multi_agent": True,
            "tools": True
        }
        
        # Register the mock adapter
        registry.register_adapter("mock_framework", mock_adapter)
        
        # Check it was registered
        adapters = registry.get_all_adapters()
        assert "mock_framework" in adapters
        
        # Check we can retrieve it
        retrieved_adapter = registry.get_adapter("mock_framework")
        assert retrieved_adapter is mock_adapter
    
    def test_get_available_frameworks(self):
        registry = AdapterRegistry()
        
        # Get available frameworks
        frameworks = registry.get_available_frameworks()
        
        # Verify the returned data
        assert isinstance(frameworks, dict)
        assert "langgraph" in frameworks
        assert "crewai" in frameworks
        
        # Check feature flags
        assert "multi_agent" in frameworks["langgraph"]
        assert frameworks["langgraph"]["multi_agent"] is True
        
        assert "multi_agent" in frameworks["crewai"]
        assert frameworks["crewai"]["multi_agent"] is True
        
        # CrewAI doesn't support parallel execution
        assert frameworks["crewai"]["parallel_execution"] is False


class TestLangGraphAdapter:
    def test_initialization(self):
        adapter = LangGraphAdapter()
        
        # Check framework name
        assert adapter.get_framework_name() == "langgraph"
        
        # Check supported features
        features = adapter.get_supported_features()
        assert features["multi_agent"] is True
        assert features["tools"] is True
        assert features["streaming"] is True
    
    def test_convert_flow(self):
        adapter = LangGraphAdapter()
        
        # Test flow data
        flow_data = {
            "name": "Test Flow",
            "agents": [
                {
                    "name": "Agent 1",
                    "model_provider": "openai",
                    "model_name": "gpt-4",
                    "tool_names": ["web_search"]
                },
                {
                    "name": "Agent 2",
                    "model_provider": "anthropic",
                    "model_name": "claude-3-opus",
                    "tool_names": ["data_analysis"]
                }
            ],
            "tools": {
                "web_search": {
                    "description": "Search the web",
                    "config": {
                        "use_async": True
                    }
                },
                "data_analysis": {
                    "description": "Analyze data",
                    "config": {
                        "streaming": True
                    }
                }
            },
            "max_steps": 5
        }
        
        # Convert flow
        converted_flow = adapter.convert_flow(flow_data)
        
        # Verify structure
        assert converted_flow["type"] == "langgraph_flow"
        assert len(converted_flow["agents"]) == 2
        assert "tools" in converted_flow
        assert "web_search" in converted_flow["tools"]
        assert "data_analysis" in converted_flow["tools"]
        assert converted_flow["max_iterations"] == 5
        
        # Verify agent conversion
        first_agent = converted_flow["agents"][0]
        assert first_agent["name"] == "Agent 1"
        assert first_agent["model_provider"] == "openai"
        assert first_agent["model_name"] == "gpt-4"
        assert "web_search" in first_agent["tools"]
        
        # Verify tool conversion
        web_search_tool = converted_flow["tools"]["web_search"]
        assert web_search_tool["description"] == "Search the web"
        assert web_search_tool["langgraph_config"]["async_execution"] is True
    
    @pytest.mark.asyncio
    async def test_execute_flow(self):
        adapter = LangGraphAdapter()
        
        # Test flow
        flow = {
            "type": "langgraph_flow",
            "agents": [
                {
                    "id": "agent-1",
                    "name": "Agent 1",
                    "model_provider": "openai",
                    "model_name": "gpt-4",
                    "tools": ["web_search"]
                }
            ],
            "tools": {
                "web_search": {
                    "description": "Search the web",
                    "langgraph_config": {
                        "async_execution": True
                    }
                }
            },
            "entry_point": "agent-1",
            "max_iterations": 3
        }
        
        # Test input
        input_data = {
            "query": "test query"
        }
        
        # Execute flow
        # We won't test the actual execution, just that it returns a result
        # since the real execution would require LangGraph to be installed
        result = await adapter.execute_flow(flow, input_data)
        
        # Verify basic structure
        assert "output" in result
        assert "execution_trace" in result
        assert "steps" in result
        
        # Check output format
        assert "content" in result["output"]
        assert isinstance(result["execution_trace"], list)
        assert len(result["execution_trace"]) > 0
    
    def test_register_tools(self):
        adapter = LangGraphAdapter()
        
        # Test tools
        tools = [
            {
                "name": "web_search",
                "description": "Search the web",
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
                "config": {
                    "use_async": True,
                    "streaming": False
                }
            },
            {
                "name": "data_analysis",
                "description": "Analyze data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "array",
                            "description": "The data to analyze"
                        }
                    },
                    "required": ["data"]
                },
                "config": {
                    "use_async": False,
                    "streaming": True
                }
            }
        ]
        
        # Register tools
        result = adapter.register_tools(tools)
        
        # Verify registration
        assert "registered_tools" in result
        assert "web_search" in result["registered_tools"]
        assert "data_analysis" in result["registered_tools"]
        
        # Verify tool configuration
        web_search = result["registered_tools"]["web_search"]
        assert web_search["description"] == "Search the web"
        assert web_search["langgraph_config"]["async_execution"] is True
        assert web_search["langgraph_config"]["streaming"] is False
        
        data_analysis = result["registered_tools"]["data_analysis"]
        assert data_analysis["description"] == "Analyze data"
        assert data_analysis["langgraph_config"]["async_execution"] is False
        assert data_analysis["langgraph_config"]["streaming"] is True


class TestCrewAIAdapter:
    def test_initialization(self):
        adapter = CrewAIAdapter()
        
        # Check framework name
        assert adapter.get_framework_name() == "crewai"
        
        # Check supported features
        features = adapter.get_supported_features()
        assert features["multi_agent"] is True
        assert features["parallel_execution"] is False
        assert features["tools"] is True
        assert features["streaming"] is False
    
    def test_convert_flow(self):
        adapter = CrewAIAdapter()
        
        # Test flow data
        flow_data = {
            "name": "Test Flow",
            "agents": [
                {
                    "name": "Researcher",
                    "description": "Research information",
                    "model_provider": "openai",
                    "model_name": "gpt-4",
                    "tool_names": ["web_search"]
                },
                {
                    "name": "Analyst",
                    "description": "Analyze information",
                    "model_provider": "anthropic",
                    "model_name": "claude-3-opus",
                    "tool_names": ["data_analysis"]
                }
            ],
            "tools": {
                "web_search": {
                    "description": "Search the web",
                    "config": {
                        "allow_delegation": True
                    }
                },
                "data_analysis": {
                    "description": "Analyze data",
                    "config": {
                        "allow_delegation": False
                    }
                }
            },
            "max_steps": 5
        }
        
        # Convert flow
        converted_flow = adapter.convert_flow(flow_data)
        
        # Verify structure
        assert converted_flow["type"] == "crewai_flow"
        assert len(converted_flow["agents"]) == 2
        assert len(converted_flow["tasks"]) == 2
        assert "tools" in converted_flow
        assert "web_search" in converted_flow["tools"]
        assert "data_analysis" in converted_flow["tools"]
        assert converted_flow["max_steps"] == 5
        
        # Verify agent conversion
        first_agent = converted_flow["agents"][0]
        assert first_agent["name"] == "Researcher"
        assert first_agent["role"] == "Research information"
        assert first_agent["model_provider"] == "openai"
        assert first_agent["model_name"] == "gpt-4"
        assert "web_search" in first_agent["tools"]
        
        # Verify tool conversion
        web_search_tool = converted_flow["tools"]["web_search"]
        assert web_search_tool["description"] == "Search the web"
        assert web_search_tool["crewai_config"]["allow_delegation"] is True
        
        data_analysis_tool = converted_flow["tools"]["data_analysis"]
        assert data_analysis_tool["description"] == "Analyze data"
        assert data_analysis_tool["crewai_config"]["allow_delegation"] is False
    
    @pytest.mark.asyncio
    async def test_execute_flow(self):
        adapter = CrewAIAdapter()
        
        # Test flow
        flow = {
            "type": "crewai_flow",
            "agents": [
                {
                    "id": "agent-1",
                    "name": "Researcher",
                    "role": "Research information",
                    "model_provider": "openai",
                    "model_name": "gpt-4",
                    "tools": ["web_search"],
                    "allow_delegation": True
                },
                {
                    "id": "agent-2",
                    "name": "Analyst",
                    "role": "Analyze information",
                    "model_provider": "anthropic",
                    "model_name": "claude-3-opus",
                    "tools": ["data_analysis"],
                    "allow_delegation": True
                }
            ],
            "tasks": [
                {
                    "id": "task-1",
                    "description": "Research the topic",
                    "agent_id": "agent-1"
                },
                {
                    "id": "task-2",
                    "description": "Analyze the research",
                    "agent_id": "agent-2"
                }
            ],
            "tools": {
                "web_search": {
                    "description": "Search the web",
                    "crewai_config": {
                        "allow_delegation": True
                    }
                },
                "data_analysis": {
                    "description": "Analyze data",
                    "crewai_config": {
                        "allow_delegation": False
                    }
                }
            },
            "max_steps": 3
        }
        
        # Test input
        input_data = {
            "query": "test query"
        }
        
        # Execute flow
        # We won't test the actual execution, just that it returns a result
        # since the real execution would require CrewAI to be installed
        result = await adapter.execute_flow(flow, input_data)
        
        # Verify basic structure
        assert "output" in result
        assert "execution_trace" in result
        assert "steps" in result
        
        # Check output format
        assert "content" in result["output"]
        assert isinstance(result["execution_trace"], list)
        assert len(result["execution_trace"]) > 0
