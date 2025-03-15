"""
Base LLM provider interface for NexusFlow.ai

This module defines the abstract base class for all LLM providers, along with
common utilities and data structures.
"""

from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMResponse:
    """Response from an LLM"""
    
    def __init__(
        self,
        content: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        usage: Optional[Dict[str, int]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an LLM response
        
        Args:
            content: Response content
            model: Name of the model that generated the response
            provider: Name of the provider (openai, anthropic, etc.)
            usage: Token usage information
            metadata: Additional metadata about the response
        """
        self.content = content
        self.model = model
        self.provider = provider
        self.usage = usage or {}
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary representation"""
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "usage": self.usage,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMResponse':
        """Create response from dictionary"""
        return cls(
            content=data.get("content", ""),
            model=data.get("model"),
            provider=data.get("provider"),
            usage=data.get("usage"),
            metadata=data.get("metadata")
        )

class Message:
    """Message for LLM conversation"""
    
    def __init__(
        self,
        role: str,
        content: str,
        name: Optional[str] = None
    ):
        """
        Initialize a message
        
        Args:
            role: Role of the message sender (system, user, assistant)
            content: Message content
            name: Name of the sender (optional)
        """
        self.role = role
        self.content = content
        self.name = name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary representation"""
        message_dict = {
            "role": self.role,
            "content": self.content
        }
        
        if self.name:
            message_dict["name"] = self.name
            
        return message_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", ""),
            name=data.get("name")
        )

class Tool:
    """Tool definition for LLM function calling"""
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any]
    ):
        """
        Initialize a tool
        
        Args:
            name: Name of the tool
            description: Description of what the tool does
            parameters: JSON Schema for the tool parameters
        """
        self.name = name
        self.description = description
        self.parameters = parameters
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary representation"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tool':
        """Create tool from dictionary"""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            parameters=data.get("parameters", {})
        )

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(
        self,
        provider_name: str,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize an LLM provider
        
        Args:
            provider_name: Name of the provider
            api_key: API key for the provider
            default_model: Default model to use
            **kwargs: Additional provider-specific options
        """
        self.provider_name = provider_name
        self.api_key = api_key
        self.default_model = default_model
        self.options = kwargs
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Tool]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response to a prompt
        
        Args:
            prompt: The prompt to generate a response for
            model: Model name (uses default_model if not provided)
            system_message: System message for the conversation
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            tools: List of tools the model can use
            **kwargs: Additional provider-specific options
            
        Returns:
            LLM response
        """
        pass
    
    @abstractmethod
    async def generate_with_messages(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Tool]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response based on a list of messages
        
        Args:
            messages: List of messages in the conversation
            model: Model name (uses default_model if not provided)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            tools: List of tools the model can use
            **kwargs: Additional provider-specific options
            
        Returns:
            LLM response
        """
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available models from this provider
        
        Returns:
            List of model information dictionaries
        """
        pass
    
    def _convert_tools_format(self, tools: List[Tool]) -> Dict[str, Any]:
        """
        Convert tools to the format expected by the provider
        
        Args:
            tools: List of tools
            
        Returns:
            Provider-specific tools format
        """
        # Default implementation - override in provider-specific classes
        return [tool.to_dict() for tool in tools]
    
    def _create_default_message_list(self, prompt: str, system_message: Optional[str] = None) -> List[Message]:
        """
        Create a default message list from a prompt and optional system message
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            
        Returns:
            List of messages
        """
        messages = []
        
        if system_message:
            messages.append(Message(role="system", content=system_message))
            
        messages.append(Message(role="user", content=prompt))
        
        return messages
    
    def _format_error_response(self, error: Exception) -> LLMResponse:
        """
        Format an error as an LLM response
        
        Args:
            error: The exception that occurred
            
        Returns:
            Error response
        """
        return LLMResponse(
            content=f"Error: {str(error)}",
            model=self.default_model,
            provider=self.provider_name,
            usage={},
            metadata={"error": str(error), "error_type": type(error).__name__}
        )

class ProviderManager:
    """Manager for LLM providers"""
    
    def __init__(self):
        """Initialize a provider manager"""
        self.providers = {}
        self.default_provider = None
    
    def register_provider(self, provider: LLMProvider, make_default: bool = False):
        """
        Register a provider
        
        Args:
            provider: The provider to register
            make_default: Whether to make this the default provider
        """
        self.providers[provider.provider_name] = provider
        
        if make_default or self.default_provider is None:
            self.default_provider = provider.provider_name
            
        logger.info(f"Registered LLM provider: {provider.provider_name}")
    
    def get_provider(self, provider_name: Optional[str] = None) -> Optional[LLMProvider]:
        """
        Get a provider by name
        
        Args:
            provider_name: Name of the provider, or None for default
            
        Returns:
            The provider, or None if not found
        """
        if provider_name is None:
            if self.default_provider is None:
                return None
            provider_name = self.default_provider
            
        return self.providers.get(provider_name)
    
    async def generate(
        self,
        prompt: str,
        provider_name: Optional[str] = None,
        model: Optional[str] = None,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Tool]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from a specific provider
        
        Args:
            prompt: The prompt to generate a response for
            provider_name: Name of the provider to use (default if None)
            model: Model name (uses provider's default if not provided)
            system_message: System message for the conversation
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            tools: List of tools the model can use
            **kwargs: Additional provider-specific options
            
        Returns:
            LLM response
            
        Raises:
            ValueError: If provider not found
        """
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name or 'default'}' not found")
            
        return await provider.generate(
            prompt=prompt,
            model=model,
            system_message=system_message,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            **kwargs
        )
    
    async def generate_with_messages(
        self,
        messages: List[Union[Message, Dict[str, Any]]],
        provider_name: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Tool]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from a specific provider using messages
        
        Args:
            messages: List of messages (can be Message objects or dicts)
            provider_name: Name of the provider to use (default if None)
            model: Model name (uses provider's default if not provided)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            tools: List of tools the model can use
            **kwargs: Additional provider-specific options
            
        Returns:
            LLM response
            
        Raises:
            ValueError: If provider not found
        """
        provider = self.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Provider '{provider_name or 'default'}' not found")
        
        # Convert dict messages to Message objects if needed
        processed_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                processed_messages.append(Message.from_dict(msg))
            else:
                processed_messages.append(msg)
                
        return await provider.generate_with_messages(
            messages=processed_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            **kwargs
        )
    
    def list_providers(self) -> List[str]:
        """
        Get a list of registered provider names
        
        Returns:
            List of provider names
        """
        return list(self.providers.keys())

# Create global instance
provider_manager = ProviderManager()
