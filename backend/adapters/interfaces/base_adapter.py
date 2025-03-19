# backend/adapters/interfaces/base_adapter.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class FrameworkAdapter(ABC):
    """Base interface for all AI orchestration framework adapters"""
    
    @abstractmethod
    def convert_flow(self, flow_config: Dict[str, Any]) -> Any:
        """Convert NexusFlow configuration to framework-specific flow"""
        pass
    
    @abstractmethod
    async def execute_flow(self, flow: Any, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a framework flow with the given input data"""
        pass
    
    @abstractmethod
    def register_tools(self, tools: List[Dict[str, Any]]) -> Any:
        """Register tools with the framework"""
        pass
        
    @abstractmethod
    def get_supported_features(self) -> Dict[str, bool]:
        """Return features supported by this framework"""
        pass
    
    @abstractmethod
    def get_framework_name(self) -> str:
        """Return the name of the framework"""
        pass
