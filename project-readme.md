# NexusFlow.ai

![NexusFlow.ai](docs/assets/logo.png)

## Dynamic Agent Orchestration

NexusFlow is a next-generation framework for building AI agent systems with dynamic, capability-driven orchestration. Unlike traditional workflow systems that rely on predefined structures, NexusFlow enables fluid intelligence networks where the execution path emerges naturally from agent capabilities and relationships.

## Key Features

- **Capability-Based Routing**: Automatically route tasks to the most suitable agents based on their capabilities
- **Dynamic Graph Generation**: Build execution graphs at runtime based on input analysis and agent capabilities
- **Autonomous Agent Decisions**: Allow agents to make their own decisions about task delegation and tool usage
- **Emergent Workflows**: Create complex workflows that emerge from simple agent interactions
- **Flexible Architecture**: Adapt to different use cases without changing the underlying system

## Installation

```bash
pip install nexusflow
```

## Quick Start

```python
import asyncio
from nexusflow.core import Agent, Flow, CapabilityType

# Create agents with different capabilities
researcher = Agent(
    name="Researcher",
    capabilities=[CapabilityType.INFORMATION_RETRIEVAL],
    model_provider="openai",
    model_name="gpt-4",
    tool_names=["web_search"]
)

analyst = Agent(
    name="Analyst",
    capabilities=[CapabilityType.DATA_ANALYSIS],
    model_provider="openai",
    model_name="gpt-4",
    tool_names=["data_analysis"]
)

writer = Agent(
    name="Writer",
    capabilities=[CapabilityType.SUMMARIZATION],
    model_provider="openai",
    model_name="gpt-4"
)

# Create tools
tools = {
    "web_search": {
        "name": "web_search",
        "description": "Search the web for information"
    },
    "data_analysis": {
        "name": "data_analysis",
        "description": "Analyze data and generate insights"
    }
}

# Create a flow with these agents
flow = Flow(
    name="Research Assistant",
    agents=[researcher, analyst, writer],
    tools=tools
)

# Execute the flow with an input query
result = await flow.execute({
    "query": "What are the environmental impacts of electric vehicles?"
})

# Print the result
print(result["output"]["content"])

# Run the async code
async def main():
    result = await flow.execute({
        "query": "What are the environmental impacts of electric vehicles?"
    })
    print(result["output"]["content"])

if __name__ == "__main__":
    asyncio.run(main())
```

## Core Concepts

### Capabilities

Capabilities represent the skills or abilities that agents possess. They are used to dynamically route tasks to the most appropriate agents.

```python
from nexusflow.core import CapabilityType

# Standard capability types
CapabilityType.REASONING         # General reasoning and problem solving
CapabilityType.INFORMATION_RETRIEVAL  # Finding and retrieving information
CapabilityType.CODE_GENERATION   # Generating and understanding code
CapabilityType.DATA_ANALYSIS     # Analyzing data and generating insights
CapabilityType.SUMMARIZATION     # Creating concise summaries
CapabilityType.PLANNING          # Creating plans and breaking down tasks
CapabilityType.COORDINATION      # Coordinating multiple agents
```

### Agents

Agents are the core entities that perform tasks. Each agent has a set of capabilities and can make autonomous decisions.

```python
from nexusflow.core import Agent

agent = Agent(
    name="Data Specialist",
    capabilities=[
        CapabilityType.DATA_ANALYSIS,
        CapabilityType.REASONING
    ],
    model_provider="anthropic",
    model_name="claude-3-opus"
)
```

### Flows

Flows orchestrate the execution of agents based on their capabilities and the input requirements.

```python
from nexusflow.core import Flow

flow = Flow(
    name="Customer Support Assistant",
    agents=[coordinator, knowledge_agent, tech_specialist, writer],
    max_steps=10
)
```

## API Usage

NexusFlow provides a simple API for integrating into your applications:

```python
from fastapi import FastAPI
from nexusflow.api import router as nexusflow_router

app = FastAPI()
app.include_router(nexusflow_router, prefix="/api/nexusflow")
```

## Advanced Features

### Dynamic Graph Building

NexusFlow builds execution graphs dynamically based on agent capabilities:

```python
from nexusflow.graph import DynamicGraphBuilder

graph_builder = DynamicGraphBuilder()
graph = graph_builder.build_graph(agents, input_data)
```

### Custom Tool Integration

Extend NexusFlow with your own tools:

```python
# Define a custom tool
my_tool = {
    "name": "image_analysis",
    "description": "Analyze an image and extract information",
    "parameters": {
        "image_url": {"type": "string", "description": "URL of the image to analyze"}
    },
    "handler": my_image_analysis_function
}

# Add to flow tools
flow = Flow(
    name="Media Analysis",
    agents=[...],
    tools={"image_analysis": my_tool}
)
```

## Examples

Check out the examples directory for complete working examples:

- `examples/research_assistant.py` - A research assistant with multiple specialists
- `examples/code_generator.py` - A code generation system with planning and implementation
- `examples/customer_support.py` - A customer support system with knowledge agents

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

NexusFlow is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Learn More

- [Documentation](https://nexusflow.ai/docs)
- [Tutorials](https://nexusflow.ai/tutorials)
- [Blog](https://nexusflow.ai/blog)
