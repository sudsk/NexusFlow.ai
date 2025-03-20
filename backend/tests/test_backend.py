# backend/tests/test_backend.py
import asyncio
import os
import sys
import json

# Add parent directory to path so we can import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.adapters.registry import get_adapter_registry
from backend.core.entities.flow import Flow
from backend.services.flow.flow_service import FlowService
from backend.services.execution.execution_service import ExecutionService
from backend.db.repositories.flow_repository import FlowRepository
from backend.db.repositories.execution_repository import ExecutionRepository
from backend.db.session import Session


async def test_adapters():
    """Test adapter registry and adapters"""
    print("\n--- Testing Adapter Registry ---")
    
    # Get adapter registry
    registry = get_adapter_registry()
    
    # Get available frameworks
    frameworks = registry.get_available_frameworks()
    print(f"Available frameworks: {', '.join(frameworks.keys())}")
    
    # Test LangGraph adapter
    print("\nTesting LangGraph adapter:")
    langgraph_adapter = registry.get_adapter("langgraph")
    print(f"Framework name: {langgraph_adapter.get_framework_name()}")
    print(f"Supported features: {langgraph_adapter.get_supported_features()}")
    
    # Test CrewAI adapter
    print("\nTesting CrewAI adapter:")
    crewai_adapter = registry.get_adapter("crewai")
    print(f"Framework name: {crewai_adapter.get_framework_name()}")
    print(f"Supported features: {crewai_adapter.get_supported_features()}")
    
    # Test flow conversion
    test_flow = {
        "name": "Test Flow",
        "description": "A test flow",
        "agents": [
            {
                "name": "Researcher",
                "description": "Researches information",
                "model_provider": "openai",
                "model_name": "gpt-4",
                "capabilities": ["information_retrieval"]
            },
            {
                "name": "Writer",
                "description": "Writes content",
                "model_provider": "anthropic",
                "model_name": "claude-3-opus",
                "capabilities": ["summarization"]
            }
        ],
        "max_steps": 10,
        "tools": {
            "web_search": {
                "name": "web_search",
                "description": "Search the web for information"
            }
        }
    }
    
    print("\nConverting test flow to LangGraph format:")
    langgraph_flow = langgraph_adapter.convert_flow(test_flow)
    print(f"LangGraph flow type: {langgraph_flow.get('type')}")
    print(f"Number of agents: {len(langgraph_flow.get('agents', []))}")
    
    print("\nConverting test flow to CrewAI format:")
    crewai_flow = crewai_adapter.convert_flow(test_flow)
    print(f"CrewAI flow type: {crewai_flow.get('type')}")
    print(f"Number of agents: {len(crewai_flow.get('agents', []))}")
    
    return True


async def test_flow_service():
    """Test flow service with in-memory repositories"""
    print("\n--- Testing Flow Service ---")
    
    # Create Flow entity
    flow = Flow(
        name="Test Flow",
        description="A test flow for the flow service",
        agents=[
            {
                "name": "Researcher",
                "description": "Researches information",
                "model_provider": "openai",
                "model_name": "gpt-4",
                "capabilities": ["information_retrieval"]
            }
        ],
        max_steps=10,
        framework="langgraph"
    )
    
    print(f"Created flow entity: {flow.name}")
    flow_dict = flow.to_dict()
    print(f"Flow has {len(flow_dict['agents'])} agents")
    print(f"Flow framework: {flow_dict['framework']}")
    
    return True


async def main():
    """Run all tests"""
    try:
        # Test adapters
        await test_adapters()
        
        # Test flow service
        await test_flow_service()
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"\nError running tests: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
