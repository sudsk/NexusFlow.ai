# backend/adapters/registry.py
from typing import Dict
from .interfaces.base_adapter import FrameworkAdapter
from .langgraph.langgraph_adapter import LangGraphAdapter
from .crewai.crewai_adapter import CrewAIAdapter

class AdapterRegistry:
    """Registry for framework adapters"""
    
    def __init__(self):
        self._adapters = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default adapters"""
        self.register_adapter("langgraph", LangGraphAdapter())
        self.register_adapter("crewai", CrewAIAdapter())
    
    def register_adapter(self, name: str, adapter: FrameworkAdapter):
        """Register a new adapter"""
        self._adapters[name] = adapter
    
    def get_adapter(self, name: str) -> FrameworkAdapter:
        """Get an adapter by name"""
        if name not in self._adapters:
            raise ValueError(f"Framework adapter '{name}' not found")
        return self._adapters[name]
    
    def get_all_adapters(self) -> Dict[str, FrameworkAdapter]:
        """Get all registered adapters"""
        return self._adapters
    
    def get_available_frameworks(self) -> Dict[str, Dict[str, bool]]:
        """Get information about available frameworks and their features"""
        return {
            name: adapter.get_supported_features() 
            for name, adapter in self._adapters.items()
        }

# Create global instance
_adapter_registry = None

def get_adapter_registry() -> AdapterRegistry:
    """Get the global adapter registry instance"""
    global _adapter_registry
    if _adapter_registry is None:
        _adapter_registry = AdapterRegistry()
    return _adapter_registry
