# NexusFlow Agent Configuration Guide

## Overview

Agents are the core components of NexusFlow that perform tasks and collaborate with each other. This guide provides detailed information on how to configure agents for optimal performance in your flows.

## Agent Configuration Options

When creating or updating an agent, you can specify the following parameters:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | Yes | - | Human-readable name of the agent |
| `agent_id` | string | No | Auto-generated | Unique ID for the agent |
| `description` | string | No | Generated from name | Description of what the agent does |
| `capabilities` | array of strings | Yes | - | List of capability types the agent possesses |
| `model_provider` | string | No | "openai" | Provider for the language model |
| `model_name` | string | No | "gpt-4" | Name of the language model |
| `system_message` | string | No | Default based on capabilities | System message for the language model |
| `temperature` | float | No | 0.7 | Temperature for generation (0.0-1.0) |
| `max_tokens` | integer | No | null | Maximum tokens to generate (null for model default) |
| `tool_names` | array of strings | No | [] | List of tool names the agent can use |
| `can_delegate` | boolean | No | true | Whether the agent can delegate to other agents |

## Capability Types

Capabilities define what an agent can do and help determine which agent should handle specific tasks. NexusFlow supports the following capability types:

| Capability Type | Description | Recommended Models | Common Tools |
|-----------------|-------------|-------------------|--------------|
| `reasoning` | General reasoning and problem solving | gpt-4, claude-3-opus | - |
| `information_retrieval` | Finding and retrieving information | gpt-4, gpt-3.5-turbo | web_search, retrieve_information |
| `code_generation` | Generating and understanding code | gpt-4, claude-3-opus | code_execution |
| `data_analysis` | Analyzing data and generating insights | gpt-4 | data_analysis |
| `summarization` | Creating concise summaries | gpt-3.5-turbo, claude-3-sonnet | - |
| `planning` | Creating plans and breaking down tasks | gpt-4, claude-3-opus | - |
| `coordination` | Coordinating multiple agents | gpt-4 | - |

## Model Providers

NexusFlow supports multiple LLM providers:

### OpenAI

```json
{
  "model_provider": "openai",
  "model_name": "gpt-4"
}
```

Available models:
- `gpt-4o` - GPT-4o model (most capable)
- `gpt-4-turbo` - GPT-4 Turbo model
- `gpt-4` - GPT-4 model
- `gpt-3.5-turbo` - GPT-3.5 Turbo model (faster, lower cost)

### Anthropic

```json
{
  "model_provider": "anthropic",
  "model_name": "claude-3-opus"
}
```

Available models:
- `claude-3-opus` - Claude 3 Opus model (most capable)
- `claude-3-sonnet` - Claude 3 Sonnet model (balanced)
- `claude-3-haiku` - Claude 3 Haiku model (fastest)
- `claude-2.1` - Claude 2.1 model
- `claude-2.0` - Claude 2.0 model

### Vertex AI (Google)

```json
{
  "model_provider": "vertex_ai",
  "model_name": "gemini-1.5-pro"
}
```

Available models:
- `gemini-1.5-pro` - Gemini 1.5 Pro model
- `gemini-1.5-flash` - Gemini 1.5 Flash model (faster)
- `gemini-pro` - Gemini Pro model
- `gemini-pro-vision` - Gemini Pro Vision model (supports images)

## System Messages

The system message instructs the agent on how to behave. While NexusFlow provides default system messages based on agent capabilities, you can customize them for more specific behavior.

### Default System Messages

Each capability type has a default system message. For example, a reasoning agent's default system message is:

```
You are a reasoning agent specialized in problem solving and logical analysis.

Your strengths:
- Breaking down complex problems into manageable parts
- Providing clear, step-by-step reasoning
- Maintaining objectivity and avoiding bias
- Drawing logical conclusions from available information
- Explaining your thought process in a transparent way

When responding:
1. Take time to understand the problem thoroughly
2. Identify key variables and constraints
3. Structure your reasoning in clear, logical steps
4. Consider alternative perspectives and approaches
5. Provide a conclusion that follows from your reasoning

Remember that the quality of your reasoning is more important than the speed of your response. It's better to be thorough and correct than quick but incomplete.
```

### Custom System Messages

To create a custom system message, consider including:

1. **Role definition**: Define the agent's identity and purpose
2. **Strengths**: List the agent's key strengths and capabilities
3. **Process**: Outline how the agent should approach tasks
4. **Guidelines**: Provide behavioral guidelines and priorities
5. **Examples**: Illustrate desired behavior with examples (optional)

Example custom system message for a research specialist:

```
You are a specialized research agent focused on environmental science.

Your strengths:
- Retrieving accurate, scientific information about environmental topics
- Distinguishing between established facts and emerging research
- Citing credible sources and explaining their relevance
- Contextualizing information with historical trends and current consensus
- Explaining complex environmental concepts clearly to non-specialists

When researching:
1. Prioritize peer-reviewed scientific sources and established authorities
2. Present balanced perspectives on controversial topics
3. Acknowledge limitations in the current scientific understanding
4. Provide context about the reliability and relevance of information
5. Organize information logically from foundational concepts to specific details

Remember to cite sources where possible and clarify when you're presenting scientific consensus versus emerging or contested views.
```

## Tools

Tools extend an agent's capabilities by allowing it to perform specific actions. To enable tools for an agent, specify their names in the `tool_names` array.

### Core Tools

| Tool Name | Description | Parameters | Suitable Capabilities |
|-----------|-------------|------------|------------------------|
| `web_search` | Search the web for information | `query`: The search query | information_retrieval |
| `data_analysis` | Analyze data and generate insights | `data`: Data to analyze<br>`analysis_type`: Type of analysis to perform | data_analysis |
| `code_execution` | Execute code in a secure sandbox | `code`: Code to execute<br>`language`: Programming language | code_generation |
| `retrieve_information` | Retrieve information from knowledge base | `query`: The retrieval query | information_retrieval |

Example agent configuration with tools:

```json
{
  "name": "Research Agent",
  "capabilities": ["information_retrieval", "reasoning"],
  "model_provider": "openai",
  "model_name": "gpt-4",
  "tool_names": ["web_search", "retrieve_information"],
  "temperature": 0.3
}
```

## Agent Delegation

Agents can delegate tasks to other agents in the flow when `can_delegate` is set to `true` (default). This enables collaborative problem-solving where agents work together based on their capabilities.

To optimize delegation:

1. Give agents complementary capabilities
2. Ensure the coordinator agent has the `coordination` capability
3. Use more specialized agents for specific tasks
4. Set appropriate `temperature` values (lower for more deterministic agents)

## Specialized Agent Types

NexusFlow provides specialized agent types that are pre-configured for specific roles:

### ReasoningAgent

```json
{
  "name": "General Reasoner",
  "agent_type": "reasoning",
  "model_provider": "openai",
  "model_name": "gpt-4",
  "temperature": 0.3
}
```

### RetrievalAgent

```json
{
  "name": "Information Retriever",
  "agent_type": "retrieval",
  "model_provider": "openai",
  "model_name": "gpt-3.5-turbo",
  "retrieval_tools": ["web_search", "retrieve_information"],
  "temperature": 0.3
}
```

### CodingAgent

```json
{
  "name": "Code Generator",
  "agent_type": "coding",
  "model_provider": "anthropic",
  "model_name": "claude-3-opus",
  "supported_languages": ["python", "javascript", "typescript", "java"],
  "temperature": 0.2
}
```

### AnalysisAgent

```json
{
  "name": "Data Analyst",
  "agent_type": "analysis",
  "model_provider": "openai",
  "model_name": "gpt-4",
  "analysis_tools": ["data_analysis", "code_execution"],
  "temperature": 0.3
}
```

## Performance Optimization

To optimize agent performance:

### Model Selection

- Use more capable models (like GPT-4 or Claude 3 Opus) for complex reasoning, coordination, and tasks requiring deep context understanding
- Use faster models (like GPT-3.5 Turbo or Claude 3 Haiku) for simpler tasks and information retrieval

### Temperature Settings

- Lower temperature (0.1-0.3): More deterministic, factual responses, good for coding, analysis, and specific tasks
- Medium temperature (0.4-0.7): Balanced creativity and consistency, good for general reasoning
- Higher temperature (0.7-1.0): More creative, diverse responses, good for creative tasks

### Token Usage

- Use appropriate `max_tokens` to limit response length when needed
- For agents that will delegate, keep `max_tokens` lower to avoid unnecessary computation
- For final output agents, use higher `max_tokens` to allow comprehensive responses

## Example Configurations

### Research Assistant Flow

```json
{
  "agents": [
    {
      "name": "Research Coordinator",
      "capabilities": ["coordination", "planning", "reasoning"],
      "model_provider": "openai",
      "model_name": "gpt-4",
      "system_message": "You are a research coordinator who helps organize research efforts and synthesize findings...",
      "temperature": 0.3,
      "can_delegate": true
    },
    {
      "name": "Information Retriever",
      "capabilities": ["information_retrieval", "reasoning"],
      "model_provider": "openai",
      "model_name": "gpt-3.5-turbo",
      "system_message": "You are an information retrieval specialist who finds factual information...",
      "temperature": 0.3,
      "tool_names": ["web_search"],
      "can_delegate": true
    },
    {
      "name": "Data Analyst",
      "capabilities": ["data_analysis", "reasoning"],
      "model_provider": "openai",
      "model_name": "gpt-4",
      "system_message": "You are a data analyst who examines data and generates insights...",
      "temperature": 0.4,
      "tool_names": ["data_analysis"],
      "can_delegate": true
    },
    {
      "name": "Content Writer",
      "capabilities": ["summarization", "reasoning"],
      "model_provider": "openai",
      "model_name": "gpt-4",
      "system_message": "You are a content writer who creates clear, comprehensive content...",
      "temperature": 0.5,
      "can_delegate": true
    }
  ]
}
```

### Code Generation Flow

```json
{
  "agents": [
    {
      "name": "Code Planner",
      "capabilities": ["planning", "reasoning"],
      "model_provider": "anthropic",
      "model_name": "claude-3-opus",
      "system_message": "You are a code planning specialist who breaks down coding tasks...",
      "temperature": 0.2,
      "can_delegate": true
    },
    {
      "name": "Code Generator",
      "capabilities": ["code_generation", "reasoning"],
      "model_provider": "anthropic",
      "model_name": "claude-3-opus",
      "system_message": "You are a code generation specialist who implements high-quality code...",
      "temperature": 0.1,
      "tool_names": ["code_execution"],
      "can_delegate": true
    },
    {
      "name": "Code Reviewer",
      "capabilities": ["code_generation", "reasoning"],
      "model_provider": "openai",
      "model_name": "gpt-4",
      "system_message": "You are a code review specialist who checks code for bugs, optimizations, and best practices...",
      "temperature": 0.3,
      "tool_names": ["code_execution"],
      "can_delegate": true
    }
  ]
}
```

## Troubleshooting

Common issues and solutions:

### Agent Not Using Tools

**Problem**: The agent has tools assigned but doesn't use them.

**Solutions**:
- Ensure the tools are correctly configured in the flow's `tools` object
- Provide more explicit instructions in the system message about tool usage
- Lower the temperature to make the agent's behavior more predictable
- Check if the agent's capabilities align with the tools

### Agent Responses Too Long or Too Short

**Problem**: Agent responses are either too verbose or too brief.

**Solutions**:
- Adjust the `max_tokens` parameter to limit or expand response length
- Update the system message with instructions about desired verbosity
- For overly verbose agents, try a lower temperature (0.1-0.3)
- For overly brief agents, try a higher temperature (0.5-0.7)

### Poor Delegation Decisions

**Problem**: Agents are making suboptimal delegation decisions.

**Solutions**:
- Review agent capabilities to ensure proper specialization
- Improve the system message for the coordinator agent with clearer delegation guidelines
- Set more specific capabilities for specialized agents
- Reduce the number of agents if the flow is too complex

### Execution Taking Too Many Steps

**Problem**: Flow execution takes too many steps to complete.

**Solutions**:
- Check for delegation loops and adjust agent capabilities
- Provide more direct instructions in the initial query
- Reduce the `max_steps` parameter to force earlier completion
- Combine related capabilities into fewer agents
- Use more capable models for complex tasks

## Best Practices

### System Message Design

- **Be specific**: Clearly define the agent's role, responsibilities, and limitations
- **Include examples**: Provide examples of desired output formatting and style
- **Define interaction guidelines**: Specify how the agent should interact with other agents and tools
- **Set priorities**: Indicate which aspects of the task are most important

Example improvement for a research agent system message:

```
You are an environmental research specialist with expertise in climate science.

Your primary responsibilities:
1. Find accurate, current information about climate science topics
2. Distinguish between scientific consensus and emerging research
3. Prioritize peer-reviewed sources over news articles or opinion pieces
4. Explain complex scientific concepts in accessible language

When you need information:
- Use the web_search tool with specific, targeted queries
- Focus on scientific databases, academic sources, and authoritative organizations
- Specify date ranges when searching for recent developments

When you find conflicting information:
- Present both perspectives clearly
- Indicate which view represents the scientific consensus
- Explain the evidence supporting different positions

FORMAT YOUR RESPONSES LIKE THIS:
1. Brief overview of the topic (1-2 paragraphs)
2. Key findings with citations
3. Areas of scientific consensus
4. Areas of ongoing research or debate
5. Practical implications
```

### Model Selection Guidelines

| Task Complexity | Time Sensitivity | Recommended Models |
|-----------------|------------------|-------------------|
| High | Low | GPT-4, Claude 3 Opus |
| High | High | GPT-4o, Claude 3 Sonnet |
| Medium | Low | GPT-4, Claude 3 Sonnet |
| Medium | High | GPT-3.5 Turbo, Claude 3 Haiku |
| Low | Low | GPT-3.5 Turbo, Claude 3 Sonnet |
| Low | High | GPT-3.5 Turbo, Claude 3 Haiku |

### Capability Combinations

Effective combinations of capabilities for specialized agents:

- **Research Agent**: `information_retrieval` + `reasoning`
- **Analyst Agent**: `data_analysis` + `reasoning`
- **Planning Agent**: `planning` + `reasoning`
- **Implementation Agent**: `code_generation` + `reasoning`
- **Coordination Agent**: `coordination` + `planning` + `reasoning`
- **Documentation Agent**: `summarization` + `reasoning`

### Security Considerations

- Limit tool permissions to only what's necessary
- Use tool-specific rate limits to prevent excessive resource usage
- Implement input validation for all user-provided data
- Consider using separate API keys for different tools and providers
- Monitor agent activities for unexpected behavior

## Advanced Configuration

### Custom Prompt Templates

You can create custom prompt templates to standardize agent interactions:

```json
{
  "name": "Specialized Researcher",
  "capabilities": ["information_retrieval", "reasoning"],
  "model_provider": "openai",
  "model_name": "gpt-4",
  "prompt_template": {
    "prefix": "As a specialized researcher, your task is to investigate: ",
    "suffix": "\n\nProvide a comprehensive analysis with citations.",
    "examples": [
      {
        "input": "What are the latest advancements in quantum computing?",
        "output": "# Quantum Computing: Latest Advancements\n\n## Recent Breakthroughs\n..."
      }
    ]
  }
}
```

### Cascading Delegation Patterns

For complex flows, consider implementing cascading delegation patterns:

1. **Coordinator** delegates to **Domain Specialists**
2. **Domain Specialists** delegate to **Task Specialists**
3. **Task Specialists** delegate to **Tool Specialists**

This hierarchical approach keeps each agent focused on its area of expertise.

### A/B Testing Different Agent Configurations

To optimize your flows, consider running A/B tests with different agent configurations:

1. Create multiple versions of your flow with different agent configurations
2. Run the same queries through each flow
3. Compare results based on:
   - Quality of output
   - Number of steps required
   - Token usage
   - Execution time
4. Iterate and refine based on the results

## Learning Resources

For more information about agent configuration, refer to these resources:

- [NexusFlow Documentation](https://docs.nexusflow.ai)
- [Agent Configuration Tutorial](https://docs.nexusflow.ai/tutorials/agent-configuration)
- [System Message Guidelines](https://docs.nexusflow.ai/guides/system-messages)
- [Model Selection Guide](https://docs.nexusflow.ai/guides/model-selection)
- [Tool Integration Guide](https://docs.nexusflow.ai/guides/tool-integration)

## Next Steps

After configuring your agents, consider:

1. Setting up appropriate [flow execution parameters](https://docs.nexusflow.ai/api/flows)
2. Implementing [error handling](https://docs.nexusflow.ai/guides/error-handling)
3. Adding [monitoring and observability](https://docs.nexusflow.ai/guides/monitoring)
4. Creating [automated tests](https://docs.nexusflow.ai/guides/testing) for your flows
