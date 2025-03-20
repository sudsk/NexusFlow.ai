# backend/adapters/registry.py
from typing import Dict
from .interfaces.base_adapter import FrameworkAdapter
from .langgraph.langgraph_adapter import LangGraphAdapter

def get_adapter_registry() -> Dict[str, FrameworkAdapter]:
    """Get the registry of framework adapters"""
    return {
        "langgraph": LangGraphAdapter(),
        # Add more adapters as they're implemented
        # "crewai": CrewAIAdapter(),
        # "autogen": AutoGenAdapter(),
    }
