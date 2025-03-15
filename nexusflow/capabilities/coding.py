"""
Coding Capability for NexusFlow.ai

This module implements the CodingCapability class, which represents
the code generation ability of agents in the NexusFlow system.
"""

from typing import Dict, List, Any, Optional, Set, Union
import logging
import re

from nexusflow.core.capability import Capability, CapabilityType

logger = logging.getLogger(__name__)

class CodingCapability(Capability):
    """
    Capability for code generation
    
    This capability enables agents to:
    - Generate code based on requirements
    - Understand and explain code functionality
    - Debug and fix issues in existing code
    - Optimize code for performance or readability
    - Translate code between programming languages
    """
    
    def __init__(self):
        """Initialize the coding capability"""
        super().__init__(
            type=CapabilityType.CODE_GENERATION.value,
            name="Code Generation",
            description="Ability to generate code based on requirements",
            requires_tools=["code_execution"],
            provides_output=["code", "explanation"],
            requires_input=["requirements"]
        )
        
        # Supported programming languages
        self.supported_languages = [
            "python", "javascript", "typescript", "java", "c++", "c#", 
            "go", "rust", "ruby", "php", "swift", "kotlin", "sql",
            "html", "css", "bash", "powershell"
        ]
        
        # Patterns that indicate coding needs
        self.coding_patterns = [
            r"(write|create|generate|implement|develop|code) .*(code|function|class|script|program|algorithm)",
            r"(write|create|generate) .* (in|using) (python|javascript|java|c\+\+|typescript|ruby|php|go|rust)",
            r"(how|can you) (write|code|implement)",
            r"(debug|fix|solve) .*(code|function|error|bug|issue|problem)",
            r"(optimize|improve|refactor|clean up) .*(code|function|performance)",
            r"(translate|convert|port) .*(code|function|program) from .* to .*",
            r"(show|give) me .*(example|code|script|snippet)",
            r"(help|assist) .* (coding|programming)"
        ]
        
        # Example use cases
        self.examples = [
            {
                "name": "Function implementation",
                "description": "Writing a function based on requirements",
                "input": "Write a Python function to calculate the Fibonacci sequence up to n terms.",
                "output": "```python\ndef fibonacci(n):\n    \"\"\"\n    Generate the Fibonacci sequence up to n terms.\n    \n    Args:\n        n (int): Number of terms to generate\n        \n    Returns:\n        list: Fibonacci sequence with n terms\n    \"\"\"\n    if n <= 0:\n        return []\n    elif n == 1:\n        return [0]\n    elif n == 2:\n        return [0, 1]\n    \n    # Initialize the sequence with the first two terms\n    sequence = [0, 1]\n    \n    # Generate the remaining terms\n    for i in range(2, n):\n        next_term = sequence[i-1] + sequence[i-2]\n        sequence.append(next_term)\n    \n    return sequence\n\n# Example usage\nif __name__ == \"__main__\":\n    n_terms = 10\n    result = fibonacci(n_terms)\n    print(f\"Fibonacci sequence with {n_terms} terms: {result}\")\n```\n\nThis function generates the Fibonacci sequence up to n terms. The Fibonacci sequence starts with 0 and 1, and each subsequent number is the sum of the two preceding ones.\n\nThe function handles edge cases:\n- If n ≤ 0, it returns an empty list\n- If n = 1, it returns [0]\n- If n = 2, it returns [0, 1]\n\nFor larger values of n, it builds the sequence iteratively by adding each new term as the sum of the previous two terms."
            },
            {
                "name": "Code debugging",
                "description": "Fixing bugs in existing code",
                "input": "Debug this JavaScript code that should sort an array of objects by a property, but it's not working: \n```javascript\nfunction sortByProperty(array, property) {\n  return array.sort(function(a, b) {\n    return a[property] < b[property];\n  });\n}\n```",
                "output": "The issue with this JavaScript code is in the comparison function used in `sort()`. Let me fix it:\n\n```javascript\nfunction sortByProperty(array, property) {\n  return array.sort(function(a, b) {\n    // Fix: Use proper comparison that returns -1, 0, or 1\n    if (a[property] < b[property]) {\n      return -1;\n    }\n    if (a[property] > b[property]) {\n      return 1;\n    }\n    return 0;\n  });\n}\n```\n\nThe problem was that the original comparison function was returning a boolean value (`true` or `false`) instead of a number. JavaScript's `sort()` method expects the comparison function to return:\n\n- A negative value if `a` should come before `b`\n- A positive value if `a` should come after `b`\n- Zero if they are equal\n\nThe original function was returning `true` (which is converted to 1) when `a[property] < b[property]`, and `false` (which is converted to 0) otherwise. This would sort elements in the wrong order.\n\nAlternatively, you can use a simpler approach that still correctly handles the comparison:\n\n```javascript\nfunction sortByProperty(array, property) {\n  return array.sort(function(a, b) {\n    return a[property] - b[property]; // This works for numeric properties\n  });\n}\n```\n\nOr for properties that might be strings:\n\n```javascript\nfunction sortByProperty(array, property) {\n  return array.sort(function(a, b) {\n    return a[property].toString().localeCompare(b[property].toString());\n  });\n}\n```"
            },
            {
                "name": "Language translation",
                "description": "Translating code between programming languages",
                "input": "Translate this Python code to JavaScript:\n```python\ndef process_data(data):\n    results = {}\n    for item in data:\n        if item['status'] == 'active':\n            category = item.get('category', 'unknown')\n            if category not in results:\n                results[category] = []\n            results[category].append(item['value'])\n    \n    # Calculate averages\n    for category, values in results.items():\n        results[category] = sum(values) / len(values)\n    \n    return results\n```",
                "output": "Here's the Python code translated to JavaScript:\n\n```javascript\nfunction processData(data) {\n  const results = {};\n  \n  // Group values by category\n  for (const item of data) {\n    if (item.status === 'active') {\n      const category = item.category || 'unknown';\n      if (!results[category]) {\n        results[category] = [];\n      }\n      results[category].push(item.value);\n    }\n  }\n  \n  // Calculate averages\n  for (const category in results) {\n    const values = results[category];\n    results[category] = values.reduce((sum, value) => sum + value, 0) / values.length;\n  }\n  \n  return results;\n}\n```\n\nKey differences explained:\n\n1. **Function naming**: Changed from snake_case (`process_data`) to camelCase (`processData`) to follow JavaScript conventions\n\n2. **Variable declarations**: Used `const` for immutable variables\n\n3. **Property access**:\n   - Python: `item['status']` or `item.get('category', 'unknown')`\n   - JavaScript: `item.status` and `item.category || 'unknown'`\n\n4. **Object property checking**:\n   - Python: `if category not in results`\n   - JavaScript: `if (!results[category])`\n\n5. **Iteration**:\n   - Python: `for category, values in results.items()`\n   - JavaScript: `for (const category in results)`\n\n6. **Average calculation**:\n   - Python: `sum(values) / len(values)`\n   - JavaScript: `values.reduce((sum, value) => sum + value, 0) / values.length`\n\nThe JavaScript version maintains the same functionality as the Python original, following JavaScript's syntax and conventions."
            }
        ]
    
    def matches_input(self, input_data: Dict[str, Any]) -> float:
        """
        Check if the input requires code generation capability
        
        Args:
            input_data: Input data to analyze
            
        Returns:
            Match score between 0.0 and 1.0
        """
        query = input_data.get("query", "").lower()
        
        # Check if any coding patterns are present
        for pattern in self.coding_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return 0.9  # High match if coding indicators are present
        
        # Check for programming language mentions
        for language in self.supported_languages:
            if language.lower() in query.lower():
                return 0.8  # Strong match if a programming language is mentioned
        
        # Check for code-related keywords
        coding_keywords = [
            "code", "function", "algorithm", "programming", "script", "method",
            "class", "object", "library", "api", "compiler", "runtime", "debugging"
        ]
        if any(keyword in query for keyword in coding_keywords):
            return 0.7  # Moderate-to-strong match for coding keywords
        
        return 0.2  # Low default match
    
    def get_prompt_enhancement(self, input_data: Dict[str, Any]) -> str:
        """
        Get prompt enhancement for coding tasks
        
        Args:
            input_data: Input data for the task
            
        Returns:
            Prompt enhancement text
        """
        # Detect if a specific language is requested
        query = input_data.get("query", "").lower()
        language = None
        
        for lang in self.supported_languages:
            if lang.lower() in query:
                language = lang
                break
        
        # Base prompt enhancement
        enhancement = """
When writing code:

1. First, understand the requirements thoroughly
2. Design a clear solution approach
3. Write code that is:
   - Readable and well-structured
   - Properly commented
   - Efficient and optimized
   - Handles edge cases and potential errors
4. Include example usage to demonstrate how the code works
5. Explain key parts of the implementation
"""
        
        # Add language-specific guidance if a language was detected
        if language:
            if language == "python":
                enhancement += """
For Python code:
- Follow PEP 8 style guidelines
- Use docstrings for functions and classes
- Prefer Pythonic approaches (list comprehensions, etc.)
- Use type hints when helpful
- Handle errors with appropriate try/except blocks
"""
            elif language in ["javascript", "typescript"]:
                enhancement += """
For JavaScript/TypeScript code:
- Use modern ES6+ syntax when appropriate
- Use const/let instead of var
- Document functions with JSDoc comments
- Consider async/await for asynchronous operations
- Handle errors properly with try/catch or Promise handling
"""
            elif language == "java":
                enhancement += """
For Java code:
- Follow standard Java naming conventions
- Use proper exception handling
- Include Javadoc comments for public methods
- Design with object-oriented principles in mind
- Consider thread safety when appropriate
"""
        
        return enhancement
    
    def get_system_message_guidance(self) -> str:
        """
        Get guidance for system message related to code generation
        
        Returns:
            System message guidance
        """
        return """
You excel at generating high-quality code. When writing code:
- Write clean, readable, and maintainable code
- Follow language-specific best practices and conventions
- Include appropriate comments and documentation
- Handle edge cases and potential errors
- Optimize for both readability and performance
- Provide explanations of key concepts and decisions
- Test the code with example inputs when possible
- Debug and fix issues methodically and thoroughly
"""
    
    def detect_programming_language(self, query: str) -> Optional[str]:
        """
        Detect the programming language requested in the query
        
        Args:
            query: The query to analyze
            
        Returns:
            Detected language or None
        """
        # Check for explicit language mentions
        for language in self.supported_languages:
            # Patterns like "in Python", "using JavaScript", etc.
            patterns = [
                f"in {language}",
                f"using {language}",
                f"with {language}",
                f"{language} code",
                f"{language} script",
                f"{language} program",
                f"{language} function",
                f"{language} class",
                f"{language} implementation"
            ]
            
            for pattern in patterns:
                if pattern.lower() in query.lower():
                    return language
        
        return None
