# NexusFlow Flow Configuration and Execution Guide

## Overview

A Flow in NexusFlow is an orchestrated sequence of agents working together to solve complex tasks. This guide explains how to configure, create, and execute flows to achieve optimal performance and reliability.

## Flow Configuration

A flow configuration defines the agents, tools, and execution parameters that determine how the flow will operate.

### Basic Structure

```json
{
  "name": "Research Assistant",
  "description": "A research assistant that helps answer complex questions",
  "agents": [
    // Array of agent configurations
  ],
  "max_steps": 10,
  "tools": {
    // Tool definitions
  }
}
```

### Configuration Options

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | Yes | - | Human-readable name of the flow |
| `description` | string | No | "" | Description of what the flow does |
| `agents` | array | Yes | - | Array of agent configurations |
| `max_steps` | integer | No | 10 | Maximum number of execution steps |
| `tools` | object | No | {} | Tool definitions available to agents |

## Agent Configuration

Each agent in the flow requires its own configuration. See the [Agent Configuration Guide](agent_configuration.md) for detailed information.

```json
{
  "name": "Research Coordinator",
  "capabilities": ["coordination", "planning", "reasoning"],
  "model_provider": "openai",
  "model_name": "gpt-4",
  "system_message": "You are a research coordinator who helps organize research efforts...",
  "temperature": 0.3,
  "tool_names": [],
  "can_delegate": true
}
```

## Tool Configuration

Tools extend agent capabilities by enabling them to perform specific actions.

```json
{
  "tools": {
    "web_search": {
      "name": "web_search",
      "description": "Search the web for information on a topic",
      "parameters": {
        "query": {"type": "string", "description": "The search query"}
      }
    },
    "data_analysis": {
      "name": "data_analysis",
      "description": "Analyze data using various techniques",
      "parameters": {
        "data": {"type": "string", "description": "Data to analyze"},
        "analysis_type": {"type": "string", "description": "Type of analysis to perform"}
      }
    }
  }
}
```

### Tool Parameters

Each tool's `parameters` object defines the inputs it accepts:

```json
"parameters": {
  "parameter_name": {
    "type": "string|number|boolean|array|object",
    "description": "Description of the parameter",
    "required": true|false,
    "default": "default value"
  }
}
```

## Flow Execution

### Execution Modes

NexusFlow supports several execution modes:

1. **Direct execution**: Execute a flow configuration directly with input
2. **Saved flow execution**: Execute a saved flow by ID
3. **Deployed flow execution**: Execute a deployed flow using its API endpoint

### Direct Execution

```http
POST /api/nexusflow/execute
```

```json
{
  "flow_config": {
    "name": "Research Assistant",
    "description": "A research assistant that helps answer complex questions",
    "agents": [
      // Agent configurations
    ],
    "max_steps": 10,
    "tools": {
      // Tool definitions
    }
  },
  "input": {
    "query": "What are the environmental impacts of electric vehicles?"
  }
}
```

### Saved Flow Execution

```http
POST /api/nexusflow/flows/{flow_id}/execute
```

```json
{
  "input": {
    "query": "What are the environmental impacts of electric vehicles?"
  },
  "options": {
    "max_steps": 12,
    "timeout": 60
  }
}
```

### Deployed Flow Execution

```http
POST /api/nexusflow/deployed/{version}/{deployment_id}/execute

Authorization: Bearer nf_a1b2c3d4e5f6g7h8i9j0
```

```json
{
  "input": {
    "query": "What are the environmental impacts of electric vehicles?"
  },
  "options": {
    "max_steps": 12,
    "timeout": 60
  }
}
```

## Execution Flow

When a flow is executed, NexusFlow follows these steps:

1. **Initialization**: The flow state is initialized with the input data
2. **Agent selection**: The initial agent is determined based on input analysis and capabilities
3. **Agent execution**: The current agent processes the input and makes a decision
4. **Decision processing**:
   - If the decision is `final`, execution completes
   - If the decision is `delegate`, execution moves to another agent
   - If the decision is `use_tool`, a tool is executed, and the result is provided to the current agent
5. **Step iteration**: Steps 3-4 repeat until a final result is reached or `max_steps` is exceeded
6. **Result generation**: The final output is returned

## Execution Options

When executing a flow, you can provide the following options:

```json
"options": {
  "max_steps": 12,       // Maximum execution steps
  "timeout": 60,         // Execution timeout in seconds
  "trace_level": "full", // Trace level: "none", "basic", "full"
  "stream": false,       // Whether to stream results as they're generated
  "async": false         // Whether to execute asynchronously
}
```

## Execution Results

Flow execution returns structured results:

```json
{
  "flow_id": "f1a2b3c4-d5e6-f7g8-h9i0-j1k2l3m4n5o6",
  "output": {
    "content": "Electric vehicles have several environmental impacts...",
    "output_type": "text",
    "metadata": {
      "agent_id": "writer",
      "agent_name": "Content Writer",
      "model": "openai/gpt-4"
    },
    "timestamp": "2025-03-15T14:25:30.123456Z"
  },
  "steps": 7,
  "execution_trace": [
    // Execution trace entries
  ],
  "timestamp": "2025-03-15T14:25:30.654321Z"
}
```

### Execution Trace

The execution trace provides detailed information about each step:

```json
"execution_trace": [
  {
    "type": "start",
    "timestamp": "2025-03-15T14:22:30.123456Z",
    "step": 1,
    "input": {"query": "What are the environmental impacts of electric vehicles?"}
  },
  {
    "type": "agent_execution",
    "agent_id": "coordinator",
    "agent_name": "Research Coordinator",
    "timestamp": "2025-03-15T14:22:35.123456Z",
    "step": 2,
    "output": {
      "content": "I'll help research the environmental impacts of electric vehicles...",
      "metadata": {
        "decision": {
          "action": "delegate",
          "target": "researcher",
          "reasoning": "Need to gather information first"
        }
      }
    }
  },
  {
    "type": "delegation",
    "agent_id": "researcher",
    "agent_name": "Information Retriever",
    "timestamp": "2025-03-15T14:22:40.123456Z",
    "step": 3,
    "input": {"query": "Research the environmental impacts of electric vehicles"}
  },
  {
    "type": "tool_execution",
    "agent_id": "researcher",
    "agent_name": "Information Retriever",
    "timestamp": "2025-03-15T14:22:45.123456Z",
    "step": 4,
    "decision": {
      "tool_name": "web_search",
      "tool_params": {
        "query": "environmental impacts electric vehicles"
      }
    },
    "output": {
      "results": [
        // Search results
      ]
    }
  }
]
```

## Flow Design Patterns

### Simple Linear Flow

Best for straightforward tasks with a clear sequence:

```
Coordinator → Researcher → Writer
```

```json
{
  "name": "Simple Research Flow",
  "description": "A straightforward research flow",
  "agents": [
    {
      "name": "Coordinator",
      "capabilities": ["coordination", "reasoning"],
      "model_provider": "openai",
      "model_name": "gpt-4"
    },
    {
      "name": "Researcher",
      "capabilities": ["information_retrieval", "reasoning"],
      "model_provider": "openai",
      "model_name": "gpt-3.5-turbo",
      "tool_names": ["web_search"]
    },
    {
      "name": "Writer",
      "capabilities": ["summarization", "reasoning"],
      "model_provider": "openai",
      "model_name": "gpt-4"
    }
  ],
  "max_steps": 5
}
```

### Hub-and-Spoke Flow

Best for complex tasks requiring multiple specialists:

```
            ┌→ Researcher →┐
Coordinator →→ Analyst    →→ Writer
            └→ Coder     →┘
```

```json
{
  "name": "Hub and Spoke Research Flow",
  "description": "A research flow with multiple specialists",
  "agents": [
    {
      "name": "Coordinator",
      "capabilities": ["coordination", "planning", "reasoning"],
      "model_provider": "openai",
      "model_name": "gpt-4"
    },
    {
      "name": "Researcher",
      "capabilities": ["information_retrieval", "reasoning"],
      "model_provider": "openai",
      "model_name": "gpt-3.5-turbo",
      "tool_names": ["web_search"]
    },
    {
      "name": "Analyst",
      "capabilities": ["data_analysis", "reasoning"],
      "model_provider": "openai",
      "model_name": "gpt-4",
      "tool_names": ["data_analysis"]
    },
    {
      "name": "Coder",
      "capabilities": ["code_generation", "reasoning"],
      "model_provider": "openai",
      "model_name": "gpt-4",
      "tool_names": ["code_execution"]
    },
    {
      "name": "Writer",
      "capabilities": ["summarization", "reasoning"],
      "model_provider": "openai",
      "model_name": "gpt-4"
    }
  ],
  "max_steps": 12
}
```

### Hierarchical Flow

Best for complex tasks with subtasks and specialized teams:

```
Coordinator
   ├→ Research Lead →→ Researcher 1 →→ Researcher 2
   ├→ Analysis Lead →→ Analyst 1    →→ Analyst 2
   └→ Content Lead  →→ Writer 1     →→ Writer 2
```

This pattern requires careful system message configuration to establish the hierarchy.

## Flow Optimization

### Performance Considerations

- **Step count**: More complex flows require higher `max_steps`
- **Model selection**: Balance capability with cost and speed
- **Tool usage**: Use tools judiciously to avoid unnecessary API calls
- **Caching**: Consider caching tool results for repeated queries

### Cost Optimization

Strategies to reduce API costs:

1. Use cheaper models for simpler tasks
2. Minimize token usage with concise system messages
3. Set appropriate `max_tokens` limits
4. Use simpler models for initial processing and more capable models for final output
5. Cache common queries and tool results

### Reliability Improvements

To improve flow reliability:

1. Implement robust error handling in tool implementations
2. Set appropriate timeouts for tools and overall execution
3. Configure retry logic for transient failures
4. Use monitoring and observability tools to identify bottlenecks
5. Set up health checks for deployed flows

## Advanced Topics

### Flow Versioning

For better lifecycle management, implement flow versioning:

```json
{
  "name": "Research Assistant",
  "version": "1.2.0",
  "description": "A research assistant that helps answer complex questions"
}
```

Semantic versioning is recommended:
- Major version: Breaking changes
- Minor version: New features, backward compatible
- Patch version: Bug fixes, backward compatible

### Flow Templates

Create reusable flow templates for common patterns:

```json
{
  "template_id": "research_assistant_v1",
  "name": "Research Assistant Template",
  "description": "Template for research assistant flows",
  "agents": [
    // Agent configurations with placeholders
  ],
  "max_steps": 10,
  "tools": {
    // Tool definitions
  },
  "variables": {
    "coordinator_model": {"default": "gpt-4", "description": "Model for the coordinator agent"},
    "max_search_results": {"default": 5, "description": "Maximum number of search results"}
  }
}
```

### Event Hooks

Configure event hooks to trigger actions during flow execution:

```json
{
  "event_hooks": {
    "on_start": {"webhook_url": "https://example.com/hooks/start"},
    "on_complete": {"webhook_url": "https://example.com/hooks/complete"},
    "on_error": {"webhook_url": "https://example.com/hooks/error"},
    "on_delegate": {"webhook_url": "https://example.com/hooks/delegate"},
    "on_tool_execution": {"webhook_url": "https://example.com/hooks/tool"}
  }
}
```

## Troubleshooting

### Common Flow Execution Issues

#### Flow Getting Stuck in Delegation Loops

**Problem**: Agents keep delegating to each other without making progress.

**Solutions**:
- Review agent system messages to include clearer decision guidelines
- Reduce the number of agents in the flow
- Set a lower `max_steps` value
- Add more specific capabilities to each agent
- Set `can_delegate: false` for terminal agents

#### Tool Execution Failures

**Problem**: Tools fail during execution.

**Solutions**:
- Check tool implementation for bugs
- Verify that tool parameters are correctly formatted
- Implement retry logic for transient failures
- Make sure agents have the correct tool usage instructions
- Check API keys and rate limits for external services

#### Flow Execution Too Slow

**Problem**: Flow execution takes too long to complete.

**Solutions**:
- Use faster models where appropriate
- Optimize tool implementations
- Reduce the number of tool calls
- Implement caching for expensive operations
- Consider parallel execution for independent tasks
- Adjust `timeout` settings for flows and tools

#### Unexpected Final Output

**Problem**: The flow's final output doesn't match expectations.

**Solutions**:
- Review the system message for the terminal agent
- Check execution trace to understand the flow path
- Ensure the right agent is making the final decision
- Add more explicit output formatting instructions
- Consider adding a post-processing step

## Monitoring and Observability

To gain insights into flow execution:

1. **Logging**: Enable detailed logging for debugging
2. **Metrics**: Track execution time, step count, and token usage
3. **Tracing**: Use execution traces to understand flow paths
4. **Alerting**: Set up alerts for failures and performance issues
5. **Visualization**: Use the flow visualization tools to understand agent interactions

## Flow Security

Security considerations for flows:

1. **Authentication**: Use API keys to control access
2. **Authorization**: Implement role-based access control for flows
3. **Isolation**: Run flows in isolated environments
4. **Rate Limiting**: Set up rate limits to prevent abuse
5. **Content Filtering**: Implement content filtering for user inputs
6. **Secret Management**: Securely manage API keys and other secrets
7. **Audit Logging**: Log all flow executions for audit purposes

## Next Steps

After mastering flow configuration and execution:

1. Learn about [flow deployment](flow_deployment.md)
2. Explore [workflow automation](workflow_automation.md)
3. Implement [CI/CD for flows](cicd_flows.md)
4. Set up [monitoring and alerting](monitoring.md)
5. Configure [access control](access_control.md)
