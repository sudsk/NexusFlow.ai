# NexusFlow Tool Integration Guide

## Overview

Tools extend agent capabilities in NexusFlow by enabling them to perform specific actions like searching the web, analyzing data, or executing code. This guide explains how to integrate, configure, and use tools within your NexusFlow applications.

## What Are Tools?

Tools are functions that agents can call to:
- Access external data sources
- Perform computations
- Interact with APIs
- Execute specialized code
- Store and retrieve information

Tools allow agents to go beyond their internal knowledge and interact with the external world.

## Core Tools

NexusFlow includes several built-in tools:

| Tool Name | Description | Common Uses | Required Capabilities |
|-----------|-------------|-------------|------------------------|
| `web_search` | Search the web for information | Research, fact-checking | information_retrieval |
| `data_analysis` | Analyze data and generate insights | Statistical analysis, data visualization | data_analysis |
| `code_execution` | Execute code in a sandbox | Testing code, data processing | code_generation |
| `retrieve_information` | Get information from knowledge bases | Domain-specific lookup | information_retrieval |

## Tool Registry

NexusFlow maintains a tool registry that tracks all available tools. The registry handles:
- Tool registration and discovery
- Parameter validation
- Execution tracking
- Error handling

## Tool Definition

A tool definition includes:

```json
{
  "name": "web_search",
  "description": "Search the web for information on a topic",
  "parameters": {
    "query": {
      "type": "string",
      "description": "The search query",
      "required": true
    },
    "num_results": {
      "type": "integer",
      "description": "Number of results to return",
      "required": false,
      "default": 5
    }
  },
  "handler": "web_search_function",
  "is_async": true,
  "category": "information",
  "tags": ["search", "web", "information"]
}
```

## Registering Tools

### Using the Tool Registry

```python
from nexusflow.tools.registry import ToolDefinition, tool_registry

# Define the tool
web_search_tool = ToolDefinition(
    name="web_search",
    description="Search the web for information on a topic",
    parameters={
        "query": {
            "type": "string",
            "description": "The search query",
            "required": True
        },
        "num_results": {
            "type": "integer",
            "description": "Number of results to return",
            "required": False,
            "default": 5
        }
    },
    handler=search_function,
    is_async=True,
    category="information",
    tags=["search", "web", "information"]
)

# Register the tool
tool_registry.register_tool(web_search_tool)
```

### Tool Implementation

```python
async def search_function(query: str, num_results: int = 5) -> Dict[str, Any]:
    """
    Search function implementation
    
    Args:
        query: Search query
        num_results: Number of results to return
        
    Returns:
        Search results
    """
    # Implementation details...
    results = await perform_search(query, num_results)
    
    return {
        "query": query,
        "results": results,
        "total_results": len(results)
    }
```

## Using Tools in Flows

To make tools available to agents in a flow:

```python
flow = Flow(
    name="Research Assistant",
    agents=[coordinator, researcher, analyst, writer],
    tools={
        "web_search": web_search_tool,
        "data_analysis": data_analysis_tool
    }
)
```

You must also specify which agents can use which tools:

```python
researcher = Agent(
    name="Researcher",
    capabilities=["information_retrieval", "reasoning"],
    model_provider="openai",
    model_name="gpt-4",
    tool_names=["web_search"]
)

analyst = Agent(
    name="Analyst",
    capabilities=["data_analysis", "reasoning"],
    model_provider="openai",
    model_name="gpt-4",
    tool_names=["data_analysis"]
)
```

## Tool Execution

When an agent decides to use a tool, the following process occurs:

1. The agent generates a decision with `action: "use_tool"`, `tool_name`, and `tool_params`
2. NexusFlow validates the tool parameters
3. The tool's handler function is called with the validated parameters
4. The result is returned to the agent for further processing

Example agent decision:

```json
{
  "action": "use_tool",
  "tool_name": "web_search",
  "tool_params": {
    "query": "environmental impacts of electric vehicles",
    "num_results": 3
  },
  "reasoning": "I need to find information about the environmental impacts of electric vehicles"
}
```

## Built-in Tool Details

### Web Search Tool

The web search tool allows agents to search the internet for information.

```json
{
  "name": "web_search",
  "description": "Search the web for information on a topic",
  "parameters": {
    "query": {
      "type": "string",
      "description": "The search query"
    },
    "num_results": {
      "type": "integer",
      "description": "Number of results to return",
      "required": false,
      "default": 5
    },
    "search_engine": {
      "type": "string",
      "description": "Search engine to use",
      "required": false,
      "default": "google",
      "enum": ["google", "bing", "duckduckgo"]
    }
  }
}
```

**Using the search tool effectively**:

1. Use specific, targeted search queries
2. Include relevant keywords and date ranges
3. Use quotes for exact phrases
4. Use site-specific searches with `site:example.com`

**System message guidance**:

```
When you need to find information online:
1. Use the web_search tool with specific, targeted queries
2. Start with broad searches, then refine based on results
3. Use quotes for exact phrases: "electric vehicle emissions study"
4. Include date ranges for recent information: "climate policy 2023"
5. Try alternative queries if initial searches don't yield useful results
```

### Data Analysis Tool

The data analysis tool allows agents to analyze data and generate insights.

```json
{
  "name": "data_analysis",
  "description": "Analyze data and generate insights",
  "parameters": {
    "data": {
      "type": "string",
      "description": "Data to analyze (CSV, JSON, or base64-encoded data)"
    },
    "analysis_type": {
      "type": "string",
      "description": "Type of analysis to perform",
      "required": false,
      "default": "descriptive",
      "enum": ["descriptive", "statistical", "correlation", "clustering", "regression"]
    },
    "format": {
      "type": "string",
      "description": "Format of the data",
      "required": false,
      "default": "auto",
      "enum": ["auto", "csv", "json", "tsv", "excel", "parquet"]
    },
    "columns": {
      "type": "array",
      "description": "Columns to include in the analysis",
      "required": false
    },
    "include_charts": {
      "type": "boolean",
      "description": "Whether to include visualizations",
      "required": false,
      "default": true
    }
  }
}
```

**Using the data analysis tool effectively**:

1. Provide data in a structured format (CSV, JSON)
2. Specify the analysis type based on the question
3. Filter to relevant columns to focus the analysis
4. Request visualizations for better understanding

**System message guidance**:

```
When analyzing data:
1. First understand the structure and content of the data
2. Choose the appropriate analysis type:
   - descriptive: For general statistics and overview
   - statistical: For hypothesis testing and significance analysis
   - correlation: For relationships between variables
   - clustering: For grouping similar data points
   - regression: For predictive relationships
3. Request visualizations when they would help understand patterns
4. Focus on relevant columns rather than analyzing all data
```

### Code Execution Tool

The code execution tool allows agents to execute code in a sandboxed environment.

```json
{
  "name": "code_execution",
  "description": "Execute code in a secure sandbox environment",
  "parameters": {
    "code": {
      "type": "string",
      "description": "Code to execute"
    },
    "language": {
      "type": "string",
      "description": "Programming language",
      "required": false,
      "default": "python",
      "enum": ["python", "javascript"]
    },
    "timeout": {
      "type": "integer",
      "description": "Maximum execution time in seconds",
      "required": false,
      "default": 5
    }
  }
}
```

**Using the code execution tool effectively**:

1. Write self-contained code that doesn't rely on external dependencies
2. Include proper error handling
3. Limit execution time for resource-intensive operations
4. Use print statements to capture output

**System message guidance**:

```
When writing code for execution:
1. Make your code self-contained and handle potential errors
2. Use print() statements to show intermediate results and final output
3. Keep code concise and focused on the specific task
4. For data processing, include sample outputs to verify correctness
5. Be aware of the execution timeout (5 seconds by default)
```

## Creating Custom Tools

You can create custom tools to extend NexusFlow's capabilities:

### 1. Define the Tool Function

```python
async def image_analysis_tool(image_url: str, analysis_type: str = "general") -> Dict[str, Any]:
    """
    Analyze an image and extract information
    
    Args:
        image_url: URL of the image to analyze
        analysis_type: Type of analysis to perform (general, text, objects, faces)
        
    Returns:
        Analysis results
    """
    # Implementation using a computer vision API
    try:
        # Download the image
        image_data = await download_image(image_url)
        
        # Perform analysis based on type
        if analysis_type == "text":
            results = await extract_text(image_data)
        elif analysis_type == "objects":
            results = await detect_objects(image_data)
        elif analysis_type == "faces":
            results = await detect_faces(image_data)
        else:  # general
            results = await analyze_image(image_data)
        
        return {
            "image_url": image_url,
            "analysis_type": analysis_type,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "image_url": image_url,
            "analysis_type": analysis_type
        }
```

### 2. Create a Tool Definition

```python
image_analysis_tool_def = ToolDefinition(
    name="image_analysis",
    description="Analyze an image and extract information",
    parameters={
        "image_url": {
            "type": "string",
            "description": "URL of the image to analyze",
            "required": True
        },
        "analysis_type": {
            "type": "string",
            "description": "Type of analysis to perform",
            "required": False,
            "default": "general",
            "enum": ["general", "text", "objects", "faces"]
        }
    },
    handler=image_analysis_tool,
    is_async=True,
    category="analysis",
    tags=["image", "vision", "analysis"]
)
```

### 3. Register the Tool

```python
tool_registry.register_tool(image_analysis_tool_def)
```

### 4. Add to Flow and Agents

```python
# Add to flow
flow = Flow(
    name="Visual Analysis Assistant",
    agents=[coordinator, vision_analyst, content_writer],
    tools={
        "web_search": web_search_tool,
        "image_analysis": image_analysis_tool_def
    }
)

# Enable for specific agents
vision_analyst = Agent(
    name="Vision Analyst",
    capabilities=["data_analysis", "reasoning"],
    model_provider="openai",
    model_name="gpt-4",
    tool_names=["image_analysis"]
)
```

## Tool Error Handling

Tools should implement robust error handling:

```python
async def web_search(query: str, num_results: int = 5) -> Dict[str, Any]:
    try:
        # Normal execution
        results = await perform_search(query, num_results)
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
    except RateLimitError as e:
        # Handle rate limiting
        return {
            "error": "Rate limit exceeded",
            "details": str(e),
            "query": query,
            "retry_after": e.retry_after
        }
    except AuthenticationError as e:
        # Handle authentication issues
        return {
            "error": "Authentication failed",
            "details": str(e),
            "query": query
        }
    except ConnectionError as e:
        # Handle connection issues
        return {
            "error": "Connection failed",
            "details": str(e),
            "query": query
        }
    except Exception as e:
        # Handle unexpected errors
        return {
            "error": "Unexpected error",
            "details": str(e),
            "query": query
        }
```

NexusFlow will pass error information back to the agent, allowing it to handle the error appropriately.

## Tool Execution Options

Tools can be configured with execution options:

```python
web_search_tool = ToolDefinition(
    name="web_search",
    # ... other parameters ...
    execution_options={
        "timeout": 10,  # Maximum execution time in seconds
        "retry_count": 3,  # Number of retries on failure
        "retry_delay": 1,  # Delay between retries in seconds
        "cache_ttl": 3600,  # Cache time-to-live in seconds
        "rate_limit": {
            "requests_per_minute": 60,
            "requests_per_day": 1000
        }
    }
)
```

## Tool Caching

NexusFlow can cache tool results to improve performance and reduce API calls:

```python
# Enable caching for the tool registry
tool_registry.enable_caching(
    cache_dir="tool_cache",
    default_ttl=3600,  # 1 hour
    max_cache_size=1024 * 1024 * 100  # 100 MB
)

# Set tool-specific cache settings
web_search_tool = ToolDefinition(
    name="web_search",
    # ... other parameters ...
    cache_settings={
        "enabled": True,
        "ttl": 1800,  # 30 minutes
        "cache_key_params": ["query"]  # Parameters to include in cache key
    }
)
```

## Tool Security

Security considerations for tools:

### 1. Input Validation

Always validate input parameters:

```python
def validate_search_query(query: str) -> str:
    """Validate and sanitize a search query"""
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[^\w\s\-\.,\?!]', '', query)
    
    # Limit length
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000]
    
    return sanitized
```

### 2. Resource Limits

Implement resource limits to prevent abuse:

```python
execution_options={
    "timeout": 5,  # Maximum execution time
    "max_output_size": 1024 * 1024,  # 1 MB
    "max_memory_usage": 100 * 1024 * 1024  # 100 MB
}
```

### 3. Authentication and Authorization

Secure external API access:

```python
def get_api_credentials():
    """Get API credentials from secure storage"""
    # In production, use a secure secret manager
    return {
        "api_key": os.environ.get("API_KEY"),
        "api_secret": os.environ.get("API_SECRET")
    }
```

### 4. Sandboxing

For code execution, use a secure sandbox:

```python
async def execute_code_in_sandbox(code: str, language: str = "python"):
    """Execute code in a secure sandbox"""
    # Use a container or VM for isolation
    result = await container.run(
        image="sandbox-image",
        command=["python", "-c", code],
        timeout=5,
        memory="100m",
        security_opt=["no-new-privileges"]
    )
    return result
```

## Tool Observability

Track tool execution for monitoring and debugging:

```python
# Enable tool execution logging
tool_registry.enable_execution_logging(
    log_file="tool_executions.log",
    log_level="INFO",
    include_params=True,
    include_results=False
)

# Get execution history
executions = tool_registry.get_execution_history(
    tool_name="web_search",
    limit=10,
    filter={"status": "success"}
)

# Get performance metrics
metrics = tool_registry.get_performance_metrics(
    tool_name="web_search",
    time_period="1d"
)
```

## Tool Integration with External Services

### API-Based Tools

Connect to external APIs:

```python
async def weather_tool(location: str, units: str = "metric") -> Dict[str, Any]:
    """Get weather information for a location"""
    api_key = os.environ.get("WEATHER_API_KEY")
    url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&units={units}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        
        return {
            "location": data["location"]["name"],
            "country": data["location"]["country"],
            "temperature": data["current"]["temp_c" if units == "metric" else "temp_f"],
            "condition": data["current"]["condition"]["text"],
            "humidity": data["current"]["humidity"],
            "wind_speed": data["current"]["wind_kph" if units == "metric" else "wind_mph"],
            "updated": data["current"]["last_updated"]
        }
```

### Database Tools

Connect to databases:

```python
async def database_query_tool(query: str, database: str = "default") -> Dict[str, Any]:
    """Execute a database query"""
    # Get database connection details from configuration
    conn_details = config.get_database_config(database)
    
    async with aiopg.create_pool(**conn_details) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                results = await cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                
                return {
                    "columns": columns,
                    "rows": results,
                    "row_count": len(results),
                    "query": query
                }
```

### File System Tools

Interact with the file system:

```python
async def file_read_tool(file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """Read a file from the file system"""
    # Validate file path to prevent path traversal
    if ".." in file_path or not file_path.startswith("/safe/"):
        raise ValueError("Invalid file path")
    
    try:
        async with aiofiles.open(file_path, mode="r", encoding=encoding) as f:
            content = await f.read()
            
            return {
                "file_path": file_path,
                "content": content,
                "size": len(content),
                "encoding": encoding
            }
    except FileNotFoundError:
        return {
            "error": "File not found",
            "file_path": file_path
        }
```

## Tool Testing

Test tools to ensure they work as expected:

```python
async def test_web_search_tool():
    """Test the web search tool"""
    # Test with valid query
    result = await tool_registry.execute_tool(
        tool_name="web_search",
        parameters={"query": "test query", "num_results": 3}
    )
    assert result.success
    assert len(result.result["results"]) == 3
    
    # Test with invalid parameters
    result = await tool_registry.execute_tool(
        tool_name="web_search",
        parameters={"query": "", "num_results": -1}
    )
    assert not result.success
    assert "error" in result.result
    
    # Test with rate limiting
    tool_registry.clear_rate_limits("web_search")
    results = await asyncio.gather(
        *(tool_registry.execute_tool("web_search", {"query": f"test {i}"})
          for i in range(100))
    )
    rate_limited = [r for r in results if not r.success and "rate limit" in r.result.get("error", "").lower()]
    assert len(rate_limited) > 0
```

## Tool Documentation

Document tools for both developers and agents:

```python
web_search_tool = ToolDefinition(
    name="web_search",
    description="Search the web for information on a topic",
    parameters={
        "query": {
            "type": "string",
            "description": "The search query",
            "required": True,
            "examples": ["climate change solutions", "renewable energy technology"]
        },
        "num_results": {
            "type": "integer",
            "description": "Number of results to return",
            "required": False,
            "default": 5,
            "minimum": 1,
            "maximum": 10
        }
    },
    usage_guide="""
    # Web Search Tool
    
    Use this tool to search the web for information on a topic.
    
    ## When to use
    - When you need to find facts or information not in your training data
    - When you need up-to-date information
    - When you need to verify claims or statements
    
    ## Tips for effective searches
    - Be specific in your search queries
    - Use quotes for exact phrases: "renewable energy growth"
    - Include relevant keywords
    
    ## Examples
    - "latest renewable energy statistics 2024"
    - "climate policy European Union"
    - "electric vehicle market share by country"
    """
)
```

## Tool Marketplace

NexusFlow will eventually support a tool marketplace where you can:
- Discover community-created tools
- Share your custom tools
- Rate and review tools
- Install tools with a single command

Stay tuned for more information on the tool marketplace.

## Best Practices

### Tool Design

1. **Single responsibility**: Each tool should do one thing well
2. **Clear parameters**: Use descriptive parameter names and documentation
3. **Robust error handling**: Handle all possible error scenarios gracefully
4. **Performance optimization**: Minimize execution time and resource usage
5. **Security first**: Validate all inputs and limit access to sensitive resources

### Tool Usage in System Messages

Provide clear instructions for agents on when and how to use tools:

```
You have access to the following tools:

1. web_search: Use this tool to search the web for information.
   Example: When you need to find facts about "renewable energy", use:
   [TOOL: web_search]
   {
     "query": "renewable energy statistics 2024",
     "num_results": 3
   }
   [/TOOL]

2. data_analysis: Use this tool to analyze data.
   Example: When you need to analyze sales data, use:
   [TOOL: data_analysis]
   {
     "data": "...",
