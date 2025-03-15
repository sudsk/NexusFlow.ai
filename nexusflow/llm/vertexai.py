"""
Vertex AI provider for NexusFlow.ai

This module implements the Vertex AI provider for accessing Google's AI models.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import os
import json
import asyncio
import base64

from .provider import LLMProvider, LLMResponse, Message, Tool, provider_manager

logger = logging.getLogger(__name__)

class VertexAIProvider(LLMProvider):
    """Provider for Google's Vertex AI models"""
    
    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        default_model: str = "gemini-1.5-pro",
        credentials_path: Optional[str] = None
    ):
        """
        Initialize Vertex AI provider
        
        Args:
            project_id: Google Cloud project ID (uses GOOGLE_CLOUD_PROJECT env var if not provided)
            location: Google Cloud region for Vertex AI
            default_model: Default model to use
            credentials_path: Path to Google Cloud credentials file (uses GOOGLE_APPLICATION_CREDENTIALS env var if not provided)
        """
        # Get project ID from environment if not provided
        if project_id is None:
            project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
            if not project_id:
                logger.warning("No Google Cloud project ID provided. Set GOOGLE_CLOUD_PROJECT environment variable.")
        
        # Get credentials path from environment if not provided
        if credentials_path is None:
            credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        
        # Initialize base provider
        super().__init__(
            provider_name="vertex_ai",
            api_key=None,  # Vertex AI uses GCP authentication, not API keys
            default_model=default_model
        )
        
        self.project_id = project_id
        self.location = location
        self.credentials_path = credentials_path
        
        # Available models
        self.available_models = [
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "context_length": 1000000, "capabilities": ["chat", "tools", "vision"]},
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "context_length": 1000000, "capabilities": ["chat", "vision"]},
            {"id": "gemini-pro", "name": "Gemini Pro", "context_length": 30720, "capabilities": ["chat", "tools"]},
            {"id": "gemini-pro-vision", "name": "Gemini Pro Vision", "context_length": 30720, "capabilities": ["chat", "vision"]},
            {"id": "text-bison@002", "name": "Text Bison", "context_length": 8192, "capabilities": ["text"]},
            {"id": "chat-bison@002", "name": "Chat Bison", "context_length": 8192, "capabilities": ["chat"]},
        ]
        
        # Try to import Vertex AI
        try:
            # We're using async, so import the async client
            import google.cloud.aiplatform as aiplatform
            from vertexai.preview.generative_models import GenerativeModel
            
            # Initialize Vertex AI
            if self.credentials_path:
                # Set credentials if provided
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path
            
            # Initialize Vertex AI with project and location
            if self.project_id:
                aiplatform.init(project=self.project_id, location=self.location)
                self.has_client = True
                self.aiplatform = aiplatform
                self.GenerativeModel = GenerativeModel
            else:
                self.has_client = False
                
        except ImportError:
            logger.warning("Vertex AI package not installed. Install it with: pip install google-cloud-aiplatform vertexai")
            self.has_client = False
        except Exception as e:
            logger.error(f"Error initializing Vertex AI client: {str(e)}")
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
                content="Vertex AI client not initialized. Please install google-cloud-aiplatform and vertexai packages and provide valid Google Cloud credentials.",
                model=model or self.default_model,
                provider=self.provider_name
            )
        
        # Use default model if not provided
        if model is None:
            model = self.default_model
        
        try:
            # We need to run this in a separate thread because Vertex AI's client is not async
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                lambda: self._generate_sync(messages, model, temperature, max_tokens, tools, **kwargs)
            )
            return result
        except Exception as e:
            logger.exception(f"Error generating response from Vertex AI: {str(e)}")
            return self._format_error_response(e)
    
    def _generate_sync(
        self,
        messages: List[Message],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        tools: Optional[List[Tool]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Synchronous implementation of generate_with_messages
        
        This is used because Vertex AI's client is not async.
        """
        try:
            import time
            from vertexai.preview.generative_models import GenerationConfig, Part, Content, FunctionDeclaration
            from google.api_core.exceptions import InvalidArgument
            
            # Create generation config
            generation_config = {
                "temperature": temperature,
                "top_p": kwargs.get("top_p", 0.95),
                "top_k": kwargs.get("top_k", 40),
            }
            
            # Add max tokens if provided
            if max_tokens is not None:
                generation_config["max_output_tokens"] = max_tokens
            
            # Instantiate the model
            model_instance = self.GenerativeModel(model)
            
            # Build contents from messages
            contents = []
            for msg in messages:
                # Convert role to Vertex AI format
                role = msg.role
                if role == "user":
                    role = "user"
                elif role == "assistant":
                    role = "model"
                elif role == "system":
                    # System messages are added as user messages with a special tag
                    role = "user"
                
                # For Gemini, we just use the text content
                contents.append(Content(
                    role=role, 
                    parts=[Part.from_text(msg.content)]
                ))
            
            # Add function declarations if tools are provided
            function_declarations = None
            if tools and model in ["gemini-1.5-pro", "gemini-pro"]:
                function_declarations = []
                for tool in tools:
                    function_declarations.append(
                        FunctionDeclaration(
                            name=tool.name,
                            description=tool.description,
                            parameters=tool.parameters
                        )
                    )
            
            # Start timing
            start_time = time.time()
            
            # Generate response
            if function_declarations:
                response = model_instance.generate_content(
                    contents,
                    generation_config=GenerationConfig(**generation_config),
                    tools=function_declarations
                )
            else:
                response = model_instance.generate_content(
                    contents,
                    generation_config=GenerationConfig(**generation_config)
                )
            
            # End timing
            end_time = time.time()
            
            # Get the text response
            content = response.text
            
            # Extract function calls if available
            function_calls = []
            if hasattr(response, "candidates") and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, "content") and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, "function_call"):
                                function_calls.append({
                                    "name": part.function_call.name,
                                    "args": part.function_call.args
                                })
            
            # Build usage information (not directly available from Vertex AI)
            usage = {}
            
            # Build metadata
            metadata = {
                "model": model,
                "latency": end_time - start_time,
                "safety_ratings": getattr(response, "safety_ratings", [])
            }
            
            if function_calls:
                metadata["function_calls"] = function_calls
            
            return LLMResponse(
                content=content,
                model=model,
                provider=self.provider_name,
                usage=usage,
                metadata=metadata
            )
            
        except Exception as e:
            logger.exception(f"Error in _generate_sync: {str(e)}")
            raise
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available models from Vertex AI
        
        Returns:
            List of model information dictionaries
        """
        # Vertex AI doesn't have a simple API to list models programmatically
        # that would work well with our structure. Return the predefined list.
        return self.available_models
    
    def _convert_tools_format(self, tools: List[Tool]) -> List[Dict[str, Any]]:
        """
        Convert tools to Vertex AI format
        
        Args:
            tools: List of tools
            
        Returns:
            Vertex AI-specific tools format
        """
        from vertexai.preview.generative_models import FunctionDeclaration
        
        function_declarations = []
        
        for tool in tools:
            function_declarations.append(
                FunctionDeclaration(
                    name=tool.name,
                    description=tool.description,
                    parameters=tool.parameters
                )
            )
        
        return function_declarations
    
    def _handle_image_input(self, content: str) -> Dict[str, Any]:
        """
        Handle image input for multimodal models
        
        Args:
            content: Content string, which might be a URL or base64 image
            
        Returns:
            Vertex AI image part
        """
        from vertexai.preview.generative_models import Part
        
        # Check if content is a URL
        if content.startswith(('http://', 'https://')):
            return Part.from_uri(content, mime_type="image/jpeg")
        
        # Check if content is a base64 image
        elif content.startswith('data:image'):
            # Extract base64 data
            mime_type = content.split(';')[0].split(':')[1]
            base64_data = content.split(',')[1]
            image_bytes = base64.b64decode(base64_data)
            return Part.from_data(image_bytes, mime_type=mime_type)
        
        # Default to text
        else:
            return Part.from_text(content)

# Register provider
def register_vertex_ai_provider(
    project_id: Optional[str] = None, 
    location: str = "us-central1",
    credentials_path: Optional[str] = None,
    make_default: bool = False
):
    """
    Register Vertex AI provider with the provider manager
    
    Args:
        project_id: Google Cloud project ID (uses GOOGLE_CLOUD_PROJECT env var if not provided)
        location: Google Cloud region for Vertex AI
        credentials_path: Path to Google Cloud credentials file (uses GOOGLE_APPLICATION_CREDENTIALS env var if not provided)
        make_default: Whether to make this the default provider
    """
    provider = VertexAIProvider(
        project_id=project_id,
        location=location,
        credentials_path=credentials_path
    )
    provider_manager.register_provider(provider, make_default=make_default)
    
    return provider
