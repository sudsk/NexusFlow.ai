"""
Retrieval Agent for NexusFlow.ai

This module defines the RetrievalAgent class, which specializes in information retrieval
tasks, such as finding facts, researching topics, and retrieving knowledge.
"""

from typing import Dict, List, Any, Optional
import logging
import json

from nexusflow.core.agent import Agent, AgentOutput
from nexusflow.core.capability import CapabilityType

logger = logging.getLogger(__name__)

class RetrievalAgent(Agent):
    """
    Agent specialized in information retrieval
    
    The RetrievalAgent focuses on retrieving relevant information from various sources,
    including:
    - Web searches
    - Knowledge bases
    - Databases
    - Document repositories
    
    It is designed to find, summarize, and present information effectively.
    """
    
    def __init__(
        self,
        name: str = "Retrieval Agent",
        agent_id: Optional[str] = None,
        model_provider: str = "openai",
        model_name: str = "gpt-4",
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        retrieval_tools: List[str] = None,
        **kwargs
    ):
        """
        Initialize a retrieval agent
        
        Args:
            name: Human-readable name of the agent
            agent_id: Unique ID for the agent (generated if not provided)
            model_provider: Provider for the language model
            model_name: Name of the language model
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            retrieval_tools: List of retrieval tool names to use
            **kwargs: Additional parameters to pass to Agent constructor
        """
        # Set default system message if not provided
        system_message = kwargs.pop('system_message', None) or self._get_default_system_message()
        
        # Set default retrieval tools if not provided
        if retrieval_tools is None:
            retrieval_tools = ["web_search", "retrieve_information"]
        
        # Set default tool names based on retrieval tools
        tool_names = kwargs.pop('tool_names', None) or retrieval_tools
        
        # Initialize base agent
        super().__init__(
            name=name,
            agent_id=agent_id,
            description="An agent specialized in information retrieval and research",
            capabilities=[CapabilityType.INFORMATION_RETRIEVAL.value, CapabilityType.REASONING.value],
            model_provider=model_provider,
            model_name=model_name,
            system_message=system_message,
            temperature=temperature,
            max_tokens=max_tokens,
            tool_names=tool_names,
            **kwargs
        )
        
        # Store retrieval-specific properties
        self.retrieval_tools = retrieval_tools
        self.retrieval_history = []
    
    def _get_default_system_message(self) -> str:
        """Get default system message for retrieval agent"""
        return """You are a retrieval agent specialized in finding, researching, and summarizing information.

Your strengths:
- Finding specific information from various sources
- Conducting thorough research on topics
- Summarizing findings clearly and concisely
- Identifying the most relevant information for a query
- Citing sources properly

When retrieving information:
1. Understand the information need thoroughly
2. Use the most appropriate search tools for the task
3. Evaluate the credibility and relevance of sources
4. Extract the most important points
5. Present information in a clear, organized manner
6. Always cite where you found the information

Remember to use search tools when you need to find specific information rather than relying solely on your internal knowledge."""
    
    async def process(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> AgentOutput:
        """
        Process input data with specialized retrieval capabilities
        
        Args:
            input_data: Input data to process
            context: Additional context for processing
            
        Returns:
            Agent output
        """
        context = context or {}
        
        # Extract query
        query = input_data.get("query", "")
        
        # If direct retrieval requested, perform it before LLM call
        if input_data.get("direct_retrieval", False) and "web_search" in self.tool_names:
            try:
                # Add retrieval context to input
                search_results = await self._perform_web_search(query)
                if search_results:
                    retrieval_context = f"\n\nRelevant information from web search:\n{search_results}"
                    input_data["query"] = f"{query}\n{retrieval_context}"
                    
                    # Record retrieval
                    self._record_retrieval("web_search", query, search_results)
            except Exception as e:
                logger.error(f"Error performing direct retrieval: {str(e)}")
        
        # Call the base agent's process method
        return await super().process(input_data, context)
    
    async def _perform_web_search(self, query: str) -> str:
        """
        Perform a web search for the query
        
        In a real implementation, this would call an actual web search API.
        This is a placeholder that simulates a web search.
        
        Args:
            query: Search query
            
        Returns:
            Search results as text
        """
        # This is a placeholder implementation
        # In a real implementation, this would use a web search API
        
        # Simulate search results
        mock_results = [
            {"title": f"Result 1 for {query}", "snippet": "This is the first result for the query..."},
            {"title": f"Result 2 for {query}", "snippet": "Another relevant piece of information about the topic..."},
            {"title": f"Result 3 for {query}", "snippet": "Some additional context about what was searched for..."}
        ]
        
        # Format results
        formatted_results = ""
        for i, result in enumerate(mock_results):
            formatted_results += f"{i+1}. {result['title']}\n   {result['snippet']}\n\n"
        
        return formatted_results
    
    def _record_retrieval(self, tool: str, query: str, results: Any) -> None:
        """
        Record a retrieval operation
        
        Args:
            tool: Name of the retrieval tool used
            query: The search query
            results: The search results
        """
        self.retrieval_history.append({
            "tool": tool,
            "query": query,
            "results_summary": results[:100] + "..." if isinstance(results, str) and len(results) > 100 else results,
            "timestamp": self._get_timestamp()
        })
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def get_retrieval_history(self) -> List[Dict[str, Any]]:
        """
        Get the retrieval history
        
        Returns:
            List of retrieval operations
        """
        return self.retrieval_history
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation"""
        agent_dict = super().to_dict()
        return {
            **agent_dict,
            "retrieval_tools": self.retrieval_tools,
            "retrieval_history_count": len(self.retrieval_history)
        }
