"""
OpenAI provider for NexusFlow.ai

This module implements the OpenAI provider for accessing OpenAI's language models.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import os
import json
import asyncio

from .provider import LLMProvider, LLMResponse, Message, Tool, provider_manager

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    """Provider for OpenAI's language models"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "gpt-4o",
        organization: Optional[str] = None
    ):
        """
        Initialize OpenAI provider
        
        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
            default_model: Default model to use
            organization: OpenAI organization ID
        """
        # Get API key from environment if not provided
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY environment variable.")
        
        # Initialize base provider
        super().__init__(
            provider_name="openai",
            api_key=api_key,
            default_model=default_model,
            organization=organization
        )
        
        # Available models
        self.available_models = [
            {"id": "gpt-4o", "name": "GPT-4o", "context_length": 128000, "capabilities": ["chat", "tools", "vision"]},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "context_length": 128000, "capabilities": ["chat", "tools"]},
            {"id": "gpt-4", "name": "GPT-4", "context_length": 8192, "capabilities": ["chat", "tools"]},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context_length": 16385, "capabilities": ["chat", "tools"]},
        ]
        
        # Try to import OpenAI
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=api_key, organization=organization)
            self.has_client = True
        except ImportError:
            logger.warning("OpenAI package not installed. Install it with: pip install openai")
            self.has_client = False
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            self.has_client = False
    
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
        # Create messages list from prompt and system message
        messages = self._create_default_message_list(prompt, system_message)
        
        # Generate with messages
        return await self.generate_with_messages(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            **kwargs
        )
    
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
        if not self.has_client:
            return LLMResponse(
                content="OpenAI client not initialized. Please install openai package and provide API key.",
                model=model or self.default_model,
                provider=self.provider_name
            )
        
        # Use default model if not provided
        if model is None:
            model = self.default_model
        
        try:
            # Convert messages to OpenAI format
            openai_messages = [msg.to_dict() for msg in messages]
            
            # Build request parameters
            request_params = {
                "model": model,
                "messages": openai_messages,
                "temperature": temperature
            }
            
            # Add max tokens if provided
            if max_tokens is not None:
                request_params["max_tokens"] = max_tokens
            
            # Add tools if provided
            if tools:
                openai_tools = self._convert_tools_format(tools)
                request_params["tools"] = openai_tools
                request_params["tool_choice"] = "auto"
            
            # Add any additional parameters
            for key, value in kwargs.items():
                request_params[key] = value
            
            # Call OpenAI API
            logger.debug(f"Calling OpenAI API with model {model}")
            start_time = asyncio.get_event_loop().time()
            response = await self.client.chat.completions.create(**request_params)
            end_time = asyncio.get_event_loop().time()
            
            # Extract content from the response
            content = response.choices[0].message.content or ""
            
            # Extract tool calls if available
            tool_calls = []
            if hasattr(response.choices[0].message, "tool_calls") and response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    tool_calls.append({
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    })
            
            # Build usage information
            usage = {}
            if hasattr(response, "usage"):
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            
            # Build metadata
            metadata = {
                "model": response.model,
                "latency": end_time - start_time,
                "finish_reason": response.choices[0].finish_reason
            }
            
            if tool_calls:
                metadata["tool_calls"] = tool_calls
            
            return LLMResponse(
                content=content,
                model=response.model,
                provider=self.provider_name,
                usage=usage,
                metadata=metadata
            )
            
        except Exception as e:
            logger.exception(f"Error generating response from OpenAI: {str(e)}")
            return self._format_error_response(e)
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available models from OpenAI
        
        Returns:
            List of model information dictionaries
        """
        if not self.has_client:
            return self.available_models
        
        try:
            # Call OpenAI API to get models
            models = await self.client.models.list()
            
            # Filter for chat models
            chat_models = []
            for model in models.data:
                if model.id.startswith("gpt-"):
                    chat_models.append({
                        "id": model.id,
                        "name": model.id,
                        # Other fields would be filled from actual API response
                    })
            
            return chat_models
            
        except Exception as e:
            logger.exception(f"Error getting available models from OpenAI: {str(e)}")
            return self.available_models
    
    def _convert_tools_format(self, tools: List[Tool]) -> List[Dict[str, Any]]:
        """
        Convert tools to OpenAI format
        
        Args:
            tools: List of tools
            
        Returns:
            OpenAI-specific tools format
        """
        openai_tools = []
        
        for tool in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            })
        
        return openai_tools

# Register provider
def register_openai_provider(api_key: Optional[str] = None, make_default: bool = True):
    """
    Register OpenAI provider with the provider manager
    
    Args:
        api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
        make_default: Whether to make this the default provider
    """
    provider = OpenAIProvider(api_key=api_key)
    provider_manager.register_provider(provider, make_default=make_default)
    
    return provider
