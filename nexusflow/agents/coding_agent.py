"""
Coding Agent for NexusFlow.ai

This module defines the CodingAgent class, which specializes in code generation,
analysis, and optimization tasks.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import re

from nexusflow.core.agent import Agent, AgentOutput
from nexusflow.core.capability import CapabilityType

logger = logging.getLogger(__name__)

class CodingAgent(Agent):
    """
    Agent specialized in code generation and programming
    
    The CodingAgent focuses on code-related tasks, including:
    - Generating code based on requirements
    - Explaining how code works
    - Debugging and fixing issues
    - Optimizing existing code
    - Translating between programming languages
    """
    
    def __init__(
        self,
        name: str = "Coding Agent",
        agent_id: Optional[str] = None,
        model_provider: str = "openai",
        model_name: str = "gpt-4",
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        supported_languages: List[str] = None,
        **kwargs
    ):
        """
        Initialize a coding agent
        
        Args:
            name: Human-readable name of the agent
            agent_id: Unique ID for the agent (generated if not provided)
            model_provider: Provider for the language model
            model_name: Name of the language model
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            supported_languages: List of programming languages this agent specializes in
            **kwargs: Additional parameters to pass to Agent constructor
        """
        # Set default system message if not provided
        system_message = kwargs.pop('system_message', None) or self._get_default_system_message()
        
        # Set default tool names if not provided
        tool_names = kwargs.pop('tool_names', None) or ["code_execution"]
        
        # Set default supported languages if not provided
        self.supported_languages = supported_languages or [
            "python", "javascript", "typescript", "java", "c++", "c#", 
            "go", "rust", "ruby", "php", "swift", "kotlin"
        ]
        
        # Initialize base agent
        super().__init__(
            name=name,
            agent_id=agent_id,
            description=f"An agent specialized in code generation and programming",
            capabilities=[CapabilityType.CODE_GENERATION.value, CapabilityType.REASONING.value],
            model_provider=model_provider,
            model_name=model_name,
            system_message=system_message,
            temperature=temperature,
            max_tokens=max_tokens,
            tool_names=tool_names,
            **kwargs
        )
        
        # Store coding-specific properties
        self.code_generations = []
    
    def _get_default_system_message(self) -> str:
        """Get default system message for coding agent"""
        return """You are a coding agent specialized in generating, analyzing, and improving code.

Your strengths:
- Writing clean, efficient, and well-documented code
- Explaining code concepts and implementations
- Debugging and fixing issues in existing code
- Optimizing code for performance and readability
- Translating between different programming languages
- Following best practices and design patterns

When writing code:
1. Understand the requirements thoroughly
2. Choose appropriate data structures and algorithms
3. Write code that is easy to read and maintain
4. Add helpful comments to explain complex parts
5. Handle edge cases and potential errors
6. Test the code with example inputs when possible

Remember that clean, readable code is often better than clever, optimized code that's hard to understand. Write code that humans can read and maintain easily."""
    
    async def process(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> AgentOutput:
        """
        Process input data with specialized coding capabilities
        
        Args:
            input_data: Input data to process
            context: Additional context for processing
            
        Returns:
            Agent output
        """
        context = context or {}
        
        # Extract query
        query = input_data.get("query", "")
        
        # If specific language is requested, format the prompt accordingly
        language = self._detect_language(query)
        if language:
            # Add language-specific instructions
            language_instructions = self._get_language_specific_instructions(language)
            if language_instructions:
                input_data["query"] = f"{query}\n\n{language_instructions}"
        
        # Call the base agent's process method
        output = await super().process(input_data, context)
        
        # Post-process the output to ensure proper code formatting
        post_processed_output = self._post_process_code_output(output)
        
        # Record code generation
        if post_processed_output != output:
            code_blocks = self._extract_code_blocks(post_processed_output.content if hasattr(post_processed_output, "content") else str(post_processed_output))
            if code_blocks:
                self._record_code_generation(language, code_blocks)
        
        return post_processed_output
    
    def _detect_language(self, query: str) -> Optional[str]:
        """
        Detect the programming language requested in the query
        
        Args:
            query: The query to analyze
            
        Returns:
            Detected language or None
        """
        # Look for explicit language mentions
        query_lower = query.lower()
        
        for language in self.supported_languages:
            # Check for patterns like "in Python", "using JavaScript", etc.
            patterns = [
                f"in {language}",
                f"using {language}",
                f"write {language}",
                f"{language} code",
                f"{language} script",
                f"{language} program"
            ]
            
            for pattern in patterns:
                if pattern.lower() in query_lower:
                    return language
        
        return None
    
    def _get_language_specific_instructions(self, language: str) -> Optional[str]:
        """
        Get language-specific instructions to include in the prompt
        
        Args:
            language: The programming language
            
        Returns:
            Language-specific instructions or None
        """
        instructions = {
            "python": """Please provide Python code that is:
- Compatible with Python 3.6+
- Well-commented with docstrings
- PEP 8 compliant
- Using proper error handling
- Modular and reusable""",
            
            "javascript": """Please provide JavaScript code that is:
- Modern (ES6+ syntax)
- Well-commented
- Following good practices (avoid global variables, use const/let appropriately)
- Browser-compatible or Node.js compatible as appropriate
- Handling potential errors properly""",
            
            "typescript": """Please provide TypeScript code that is:
- Type-safe with proper interfaces and types
- Modern (ES6+ syntax)
- Well-commented
- Following good practices
- Handling potential errors properly""",
            
            "java": """Please provide Java code that is:
- Following Java conventions
- Well-commented with Javadoc
- Object-oriented and modular
- Handling exceptions properly
- Efficient and maintainable"""
        }
        
        return instructions.get(language.lower())
    
    def _post_process_code_output(self, output: Union[AgentOutput, str]) -> Union[AgentOutput, str]:
        """
        Post-process the output to ensure proper code formatting
        
        Args:
            output: The output to process
            
        Returns:
            Processed output
        """
        # Handle different output types
        if isinstance(output, AgentOutput):
            content = output.content
            if not content:
                return output
            
            # Process content and update output
            processed_content = self._ensure_proper_code_blocks(content)
            if processed_content != content:
                # Create a new output with processed content
                new_output = AgentOutput(
                    content=processed_content,
                    output_type=output.output_type,
                    metadata=output.metadata
                )
                return new_output
            
            return output
        
        elif isinstance(output, str):
            return self._ensure_proper_code_blocks(output)
        
        return output
    
    def _ensure_proper_code_blocks(self, content: str) -> str:
        """
        Ensure code is properly formatted in markdown code blocks
        
        Args:
            content: The content to process
            
        Returns:
            Processed content
        """
        # Fix missing language tags in code blocks
        def replace_code_block(match):
            code_block = match.group(1)
            
            # Check if there's already a language specified
            if not re.match(r'```[a-zA-Z0-9]+', match.group(0)):
                # Try to detect the language
                if 'def ' in code_block or 'import ' in code_block or 'class ' in code_block:
                    return f"```python\n{code_block}\n```"
                elif 'function ' in code_block or 'const ' in code_block or 'let ' in code_block:
                    return f"```javascript\n{code_block}\n```"
                elif 'public class ' in code_block or 'private ' in code_block:
                    return f"```java\n{code_block}\n```"
                else:
                    return f"```\n{code_block}\n```"
            
            return match.group(0)
        
        # Fix code blocks without proper markdown
        fixed_content = re.sub(r'```(.*?)```', replace_code_block, content, flags=re.DOTALL)
        
        # Find potential code that's not in code blocks
        lines = fixed_content.split('\n')
        in_code_block = False
        result_lines = []
        potential_code_block = []
        
        for line in lines:
            if line.startswith('```'):
                in_code_block = not in_code_block
                result_lines.append(line)
                
                # If we just closed a code block and have potential code, clear it
                if not in_code_block:
                    potential_code_block = []
                continue
            
            if in_code_block:
                result_lines.append(line)
                continue
            
            # Check if line looks like code
            if (line.startswith('    ') and 
                not line.startswith('    -') and 
                not line.startswith('    *')):
                potential_code_block.append(line)
            else:
                # If we have accumulated potential code and now hit a non-code line
                if potential_code_block and len(potential_code_block) > 3:
                    # Insert a code block before the accumulated lines
                    result_lines.append('```')
                    result_lines.extend(potential_code_block)
                    result_lines.append('```')
                    potential_code_block = []
                else:
                    # Just add the accumulated lines as is
                    result_lines.extend(potential_code_block)
                    potential_code_block = []
                
                result_lines.append(line)
        
        # Add any remaining potential code
        if potential_code_block and len(potential_code_block) > 3:
            result_lines.append('```')
            result_lines.extend(potential_code_block)
            result_lines.append('```')
        else:
            result_lines.extend(potential_code_block)
        
        return '\n'.join(result_lines)
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """
        Extract code blocks from content
        
        Args:
            content: The content to process
            
        Returns:
            List of code blocks with language and code
        """
        # Extract code blocks with language
        code_blocks = []
        for match in re.finditer(r'```(?P<lang>[a-zA-Z0-9]*)\n(?P<code>.*?)\n```', content, re.DOTALL):
            lang = match.group('lang') or 'text'
            code = match.group('code')
            code_blocks.append({
                'language': lang,
                'code': code
            })
        
        return code_blocks
    
    def _record_code_generation(self, language: Optional[str], code_blocks: List[Dict[str, str]]) -> None:
        """
        Record a code generation
        
        Args:
            language: The programming language
            code_blocks: The generated code blocks
        """
        self.code_generations.append({
            "language": language or "unknown",
            "code_blocks": code_blocks,
            "timestamp": self._get_timestamp()
        })
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def get_code_generations(self) -> List[Dict[str, Any]]:
        """
        Get the code generation history
        
        Returns:
            List of code generations
        """
        return self.code_generations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation"""
        agent_dict = super().to_dict()
        return {
            **agent_dict,
            "supported_languages": self.supported_languages,
            "code_generations_count": len(self.code_generations)
        }
