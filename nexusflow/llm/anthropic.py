"""
Anthropic provider for NexusFlow.ai

This module implements the Anthropic provider for accessing Claude models.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import os
import json
import asyncio

from .provider import LLMProvider, LLMResponse, Message, Tool, provider_manager

logger = logging.getLogger(__name__)

class AnthropicProvider(LLMProvider):
    """Provider for Anthropic's Claude models"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "claude-3-opus-20240229"
    ):
        """
        Initialize Anthropic provider
        
        Args:
            api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)
            default_model: Default model to use
        """
        # Get API key from environment if not provided
        if api_key is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning("No Anthropic API key provided. Set ANTHROPIC_API_KEY environment variable.")
        
        # Initialize base provider
        super().__init__(
            provider_name="anthropic",
            api_key=api_key,
            default_model=default_model
        )
        
        # Available models
        self.available_models = [
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "context_length": 200000, "capabilities": ["chat", "tools", "vision"]},
            {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "context_length": 200000, "capabilities": ["chat", "tools", "vision"]},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "context_length": 200000, "capabilities": ["chat", "tools", "vision"]},
            {"id": "claude-2.1", "name": "Claude 2.1", "context_length": 200000, "capabilities": ["chat"]},
            {"id": "claude-2.0", "name": "Claude 2.0", "context_length": 100000, "capabilities": ["chat"]},
        ]
        
        # Try to import Anthropic
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
            self.has_client = True
            self.anthropic = anthropic  # Keep reference to access constants
        except ImportError:
            logger.warning("Anthropic package not installed. Install it with: pip install anthropic")
            self.has_client = False
        except Exception as e:
            logger.error(f"Error initializing Anthropic client: {str(e)}")
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
                content="Anthropic client not initialized. Please install anthropic package and provide API key.",
                model=model or self.default_model,
                provider=self.provider_name
            )
        
        # Use default model if not provided
        if model is None:
            model = self.default_model
        
        try:
            # Convert messages to Anthropic format
            anthropic_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    # System messages are handled separately in Anthropic API
                    continue
                elif msg.role == "user":
                    anthropic_messages.append({"role": "user", "content": msg.content})
                elif msg.role == "assistant":
                    anthropic_messages.append({"role": "assistant", "content": msg.content})
                else:
                    # Convert other roles to user messages with prefixes
                    anthropic_messages.append({"role": "user", "content": f"{msg.role}: {msg.content}"})
            
            # Extract system message if present
            system_message = None
            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                    break
            
            # Build request parameters
            request_params = {
                "model": model,
                "messages": anthropic_messages,
                "temperature": temperature
            }
            
            # Add system message if available
            if system_message:
                request_params["system"] = system_message
            
            # Add max tokens if provided
            if max_tokens is not None:
                request_params["max_tokens"] = max_tokens
            else:
                request_params["max_tokens"] = 4096  # Default max tokens
            
            # Add tools if provided and model supports them
            if tools and any("tools" in model_info.get("capabilities", []) for model_info in self.available_models if model_info["id"] == model):
                anthropic_tools = self._convert_tools_format(tools)
                request_params["tools"] = anthropic_tools
            
            # Add any additional parameters
            for key, value in kwargs.items():
                request_params[key] = value
            
            # Call Anthropic API
            logger.debug(f"Calling Anthropic API with model {model}")
            start_time = asyncio.get_event_loop().time()
            response = await self.client.messages.create(**request_params)
            end_time = asyncio.get_event_loop().time()
            
            # Extract content from the response
            content = response.content[0].text
            
            # Extract tool calls if available
            tool_calls = []
            if hasattr(response, "tool_use") and response.tool_use:
                for tool_use in response.tool_use:
                    tool_calls.append({
                        "id": tool_use.id,
                        "name": tool_use.name,
                        "input": tool_use.input
                    })
            
            # Build usage information
            usage = {}
            if hasattr(response, "usage"):
                usage = {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            
            # Build metadata
            metadata = {
                "model": response.model,
                "latency": end_time - start_time,
                "stop_reason": response.stop_reason,
                "stop_sequence": response.stop_sequence
            }
            
            if tool_calls:
