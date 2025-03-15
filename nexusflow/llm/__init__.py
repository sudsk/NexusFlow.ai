"""
LLM providers for NexusFlow.ai

This package contains integrations with various LLM providers:
- Provider: Base interface for LLM providers
- OpenAI: Integration with OpenAI models
- Anthropic: Integration with Anthropic Claude models
- Vertex AI: Integration with Google's Vertex AI platform
"""

from nexusflow.llm.provider import (
    LLMProvider, 
    LLMResponse, 
    Message, 
    Tool, 
    ProviderManager, 
    provider_manager
)
from nexusflow.llm.openai import OpenAIProvider, register_openai_provider
from nexusflow.llm.anthropic import AnthropicProvider, register_anthropic_provider
from nexusflow.llm.vertexai import VertexAIProvider, register_vertex_ai_provider

# Register default providers based on environment variables
import os

# Register OpenAI provider if API key is available
if os.environ.get("OPENAI_API_KEY"):
    try:
        register_openai_provider(make_default=True)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to register OpenAI provider: {str(e)}")

# Register Anthropic provider if API key is available
if os.environ.get("ANTHROPIC_API_KEY"):
    try:
        register_anthropic_provider(make_default=False)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to register Anthropic provider: {str(e)}")

# Register Vertex AI provider if project ID is available
if os.environ.get("GOOGLE_CLOUD_PROJECT"):
    try:
        register_vertex_ai_provider(make_default=False)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to register Vertex AI provider: {str(e)}")

__all__ = [
    # Provider components
    'LLMProvider',
    'LLMResponse',
    'Message',
    'Tool',
    'ProviderManager',
    'provider_manager',
    
    # Provider implementations
    'OpenAIProvider',
    'register_openai_provider',
    'AnthropicProvider',
    'register_anthropic_provider',
    'VertexAIProvider',
    'register_vertex_ai_provider',
]
