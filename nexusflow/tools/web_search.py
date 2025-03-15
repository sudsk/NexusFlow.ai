"""
Web Search Tool for NexusFlow.ai

This module provides a tool for searching the web for information.
"""

import logging
import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
import re
from datetime import datetime

from .registry import ToolDefinition, ToolResult, tool_registry

logger = logging.getLogger(__name__)

class WebSearchTool:
    """Tool for searching the web for information"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        search_engine: str = "google", 
        num_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ):
        """
        Initialize a web search tool
        
        Args:
            api_key: API key for the search engine (uses SERP_API_KEY env var if not provided)
            search_engine: Search engine to use (google, bing, etc.)
            num_results: Default number of results to return
            include_domains: List of domains to include in search
            exclude_domains: List of domains to exclude from search
        """
        # Get API key from environment if not provided
        if api_key is None:
            api_key = os.environ.get("SERP_API_KEY")
            if not api_key:
                logger.warning("No SERP API key provided. Web search will use mock results.")
        
        self.api_key = api_key
        self.search_engine = search_engine
        self.num_results = num_results
        self.include_domains = include_domains or []
        self.exclude_domains = exclude_domains or []
        
        # Cache for recent searches to avoid duplicate API calls
        self.cache = {}
        self.cache_ttl = 3600  # Cache TTL in seconds (1 hour)
        
        # Register the tool
        self._register_tool()
    
    def _register_tool(self):
        """Register the web search tool with the registry"""
        tool_def = ToolDefinition(
            name="web_search",
            description="Search the web for information on a topic",
            parameters={
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return",
                    "required": False,
                    "default": self.num_results
                },
                "search_engine": {
                    "type": "string",
                    "description": "Search engine to use",
                    "required": False,
                    "default": self.search_engine,
                    "enum": ["google", "bing", "duckduckgo"]
                },
                "include_domain": {
                    "type": "string",
                    "description": "Domain to include in search results",
                    "required": False
                },
                "exclude_domain": {
                    "type": "string",
                    "description": "Domain to exclude from search results",
                    "required": False
                }
            },
            handler=self.search,
            is_async=True,
            category="information",
            tags=["search", "web", "information"]
        )
        
        tool_registry.register_tool(tool_def)
    
    async def search(
        self,
        query: str,
        num_results: int = None,
        search_engine: Optional[str] = None,
        include_domain: Optional[str] = None,
        exclude_domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search the web for information
        
        Args:
            query: Search query
            num_results: Number of results to return
            search_engine: Search engine to use
            include_domain: Domain to include in search results
            exclude_domain: Domain to exclude from search results
            
        Returns:
            Search results
        """
        # Use default values if not provided
        num_results = num_results or self.num_results
        search_engine = search_engine or self.search_engine
        
        # Process include/exclude domains
        include_domains = self.include_domains.copy()
        if include_domain:
            include_domains.append(include_domain)
            
        exclude_domains = self.exclude_domains.copy()
        if exclude_domain:
            exclude_domains.append(exclude_domain)
        
        # Build search key for caching
        search_key = f"{query}|{num_results}|{search_engine}|{','.join(include_domains)}|{','.join(exclude_domains)}"
        
        # Check cache
        cache_entry = self.cache.get(search_key)
        if cache_entry and (datetime.utcnow().timestamp() - cache_entry["timestamp"]) < self.cache_ttl:
            return cache_entry["results"]
        
        try:
            # Call the search API or use mock results if no API key
            if self.api_key:
                results = await self._api_search(
                    query=query,
                    num_results=num_results,
                    search_engine=search_engine,
                    include_domains=include_domains,
                    exclude_domains=exclude_domains
                )
            else:
                results = self._mock_search(
                    query=query,
                    num_results=num_results
                )
            
            # Cache results
            self.cache[search_key] = {
                "results": results,
                "timestamp": datetime.utcnow().timestamp()
            }
            
            return results
            
        except Exception as e:
            logger.exception(f"Error searching web: {str(e)}")
            # Return error message
            return {
                "error": f"Error searching web: {str(e)}",
                "query": query,
                "results": []
            }
    
    async def _api_search(
        self,
        query: str,
        num_results: int,
        search_engine: str,
        include_domains: List[str],
        exclude_domains: List[str]
    ) -> Dict[str, Any]:
        """
        Call the search API
        
        Args:
            query: Search query
            num_results: Number of results to return
            search_engine: Search engine to use
            include_domains: Domains to include in search
            exclude_domains: Domains to exclude from search
            
        Returns:
            Search results
        """
        # In a real implementation, this would call a real search API
        # For now, use a mock implementation to simulate API results
        
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        # Add domain filters to query if needed
        full_query = query
        if include_domains:
            site_filters = " OR ".join([f"site:{domain}" for domain in include_domains])
            full_query += f" ({site_filters})"
        
        if exclude_domains:
            for domain in exclude_domains:
                full_query += f" -site:{domain}"
        
        # Get mock results
        mock_results = self._mock_search(query, num_results)
        
        # Add API-specific metadata
        mock_results["api_metadata"] = {
            "search_engine": search_engine,
            "full_query": full_query,
            "api_key": f"{self.api_key[:5]}..." if self.api_key else None
        }
        
        return mock_results
    
    def _mock_search(self, query: str, num_results: int) -> Dict[str, Any]:
        """
        Generate mock search results
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            Mock search results
        """
        # Create predictable but varied mock results based on query
        # This makes the mock results consistent for the same query
        
        # Extract keywords from query
        keywords = re.findall(r'\w+', query.lower())
        keywords = [k for k in keywords if len(k) > 3 and k not in ["what", "when", "where", "which", "who", "why", "how", "the", "and", "for", "that"]]
        
        if not keywords:
            keywords = ["topic"]
        
        # Generate mock results
        results = []
        domains = [
            "wikipedia.org",
            "example.com",
            "reference.site",
            "news.info",
            "academic.edu",
            "research.org",
            "blogs.net",
            "knowledge.com",
            "expert.info",
            "facts.site"
        ]
        
        for i in range(min(num_results, 10)):
            # Use modulo to cycle through keywords and domains
            keyword = keywords[i % len(keywords)]
            domain = domains[i % len(domains)]
            
            result = {
                "position": i + 1,
                "title": f"{keyword.title()} - Information and Facts | {domain}",
                "link": f"https://www.{domain}/articles/{keyword}",
                "snippet": f"Comprehensive information about {keyword}. Learn about the latest research, facts, and details related to {query}.",
                "source": domain,
                "date": None
            }
            
            results.append(result)
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results),
            "search_time": 0.25
        }

# Create a global instance
web_search_tool = WebSearchTool()

# Export the tool
__all__ = ["WebSearchTool", "web_search_tool"]
