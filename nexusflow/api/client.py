# nexusflow/api/client.py
import httpx
from typing import Dict, Any, Optional

class NexusFlowClient:
    """Client for integrating with NexusFlow from external applications"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """Initialize the client"""
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    async def execute_flow(self, flow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a deployed flow"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/nexusflow/flows/{flow_id}/execute",
                json=input_data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def list_flows(self) -> Dict[str, Any]:
        """List all available flows"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/nexusflow/flows",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_flow_details(self, flow_id: str) -> Dict[str, Any]:
        """Get details of a specific flow"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/nexusflow/flows/{flow_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
