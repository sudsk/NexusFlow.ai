# NexusFlow Capabilities Guide

## Overview

Capabilities are the foundation of NexusFlow's dynamic agent orchestration system. They define what agents can do and help automatically route tasks to the most appropriate agents. This guide explains the capabilities system and how to use it effectively in your flows.

## What Are Capabilities?

A capability represents a specific skill or ability that an agent possesses. Capabilities are used to:

1. Determine which agent should handle a specific task
2. Allow agents to make informed delegation decisions
3. Create a dynamic, flexible workflow that adapts to different inputs
4. Build specialized agents with complementary skills

## Core Capabilities

NexusFlow includes the following built-in capabilities:

| Capability Type | ID | Description | Example Skills |
|-----------------|-------------|-------------|----------------|
| General Reasoning | `reasoning` | Problem solving and logical analysis | Critical thinking, deduction, inference |
| Information Retrieval | `information_retrieval` | Finding and retrieving information | Web search, knowledge base querying |
| Code Generation | `code_generation` | Writing and understanding code | Programming, debugging, optimization |
| Data Analysis | `data_analysis` | Analyzing data and generating insights | Statistical analysis, data visualization |
| Summarization | `summarization` | Creating concise summaries | Content distillation, report generation |
| Planning | `planning` | Creating plans and breaking down tasks | Task decomposition, sequencing, prioritization |
| Coordination | `coordination` | Coordinating multiple agents | Task delegation, synthesis of agent outputs |

## Capability Registry

NexusFlow maintains a capability registry that tracks which agents have which capabilities. When a task requires a specific capability, the system automatically routes it to the agent with the highest capability score.

### Capability Scoring

Each agent's capability is assigned a score (0.0 to 1.0) indicating its proficiency. Higher scores indicate greater proficiency.

```json
{
  "agent_id": "research_specialist",
  "capability_type": "information_retrieval",
  "score": 0.9,
  "metadata": {
    "model": "openai/gpt-4",
    "temperature": 0.3
  }
}
```

The scoring system allows for specialization and prioritization, ensuring tasks are routed to the most suitable agent.

## Registering Agent Capabilities

Capabilities are registered when an agent is created:

```python
from nexusflow.core.agent import Agent
from nexusflow.core.capability import CapabilityType

researcher = Agent(
    name="Researcher",
    capabilities=[CapabilityType.INFORMATION_RETRIEVAL.value, CapabilityType.REASONING.value],
    model_provider="openai",
    model_name="gpt-4",
    system_message="You are a research specialist...",
    temperature=0.3,
    tool_names=["web_search", "retrieve_information"]
)
```

This registers the agent with the `information_retrieval` and `reasoning` capabilities in the capability registry.

## Input Analysis and Capability Detection

When a flow receives input, NexusFlow analyzes it to determine which capabilities are required:

```python
required_capabilities = capability_registry.analyze_required_capabilities(input_data)
```

This analysis uses heuristics and patterns to identify the capabilities needed for the task. For example:

- "Write a Python function that..." → `code_generation`
- "Research the history of..." → `information_retrieval`
- "Analyze this dataset and..." → `data_analysis`
- "Create a plan for..." → `planning`

## Capability-Based Routing

Based on the required capabilities, NexusFlow routes the task to the most suitable agent:

```python
primary_capability = required_capabilities[0]
agent_id = capability_registry.get_best_agent_for_capability(primary_capability)
```

This dynamic routing is what allows NexusFlow to handle a wide range of tasks without predefined workflows.

## Extending the Capability System

### Creating Custom Capabilities

You can create custom capabilities for specialized domains:

```python
from nexusflow.core.capability import Capability

medical_diagnosis_capability = Capability(
    type="medical_diagnosis",
    name="Medical Diagnosis",
    description="Ability to analyze medical symptoms and suggest potential diagnoses",
    provides_output=["diagnosis", "recommendations"],
    requires_input=["symptoms", "patient_history"]
)

capability_registry.register_capability_definition(medical_diagnosis_capability)
```

### Capability Matching Strategies

NexusFlow supports several capability matching strategies:

1. **Best Match**: Route to the agent with the highest score for the primary capability (default)
2. **Multi-Capability**: Route to the agent that best satisfies multiple required capabilities
3. **Specialized First**: Prioritize specialized agents over generalists
4. **Fallback Chain**: Try specialized agents first, then fall back to generalists

```python
flow = Flow(
    name="Medical Assistant",
    capability_matching="multi_capability",
    agents=[...],
    max_steps=10
)
```

## Capability Definitions

A capability definition includes the following components:

```json
{
  "type": "data_analysis",
  "name": "Data Analysis",
  "description": "Ability to analyze data and generate insights",
  "parameters": {
    "analysis_depth": {
      "description": "Depth of analysis",
      "type": "string",
      "enum": ["basic", "intermediate", "advanced"]
    }
  },
  "requires_tools": ["data_analysis", "code_execution"],
  "provides_output": ["analysis", "insights", "visualization"],
  "requires_input": ["data"],
  "examples": [
    {
      "name": "Basic analysis",
      "input": "Analyze this sales data",
      "output": "Sales Analysis Report..."
    }
  ]
}
```

## Capability Matrices

A capability matrix helps visualize the capabilities of different agents in a flow:

| Agent | reasoning | information_retrieval | code_generation | data_analysis | summarization | planning | coordination |
|-------|-----------|----------------------|----------------|---------------|--------------|----------|--------------|
| Coordinator | 0.8 | 0.4 | 0.0 | 0.0 | 0.5 | 0.9 | 0.9 |
| Researcher | 0.7 | 0.9 | 0.0 | 0.4 | 0.6 | 0.0 | 0.0 |
| Analyst | 0.8 | 0.3 | 0.5 | 0.9 | 0.5 | 0.0 | 0.0 |
| Coder | 0.7 | 0.2 | 0.9 | 0.5 | 0.3 | 0.0 | 0.0 |
| Writer | 0.6 | 0.4 | 0.0 | 0.0 | 0.9 | 0.0 | 0.0 |

This matrix helps identify gaps and overlaps in your agent capabilities.

## Capability-Driven System Messages

System messages should align with an agent's capabilities. For example, a `data_analysis` agent might have a system message like:

```
You are a data analysis specialist with the following capabilities:

1. Analyzing numerical data to identify patterns and trends
2. Creating visualizations to represent data insights
3. Performing statistical analysis to test hypotheses
4. Interpreting results and explaining their significance

When analyzing data:
- First understand the structure and content of the data
- Identify appropriate analytical techniques based on data type and question
- Apply rigorous statistical methods when appropriate
- Present findings clearly with supporting evidence
- Visualize results when it aids understanding
- Acknowledge limitations and assumptions in your analysis

When you receive raw data or analysis requests, use the data_analysis tool to perform calculations and generate insights.
```

## Tool-Capability Relationships

Capabilities often require specific tools to be fully effective:

| Capability | Recommended Tools |
|------------|-------------------|
| information_retrieval | web_search, retrieve_information |
| code_generation | code_execution |
| data_analysis | data_analysis, code_execution |
| summarization | None (built-in agent capability) |
| planning | None (built-in agent capability) |
| coordination | None (built-in agent capability) |

Make sure agents have access to the tools needed for their capabilities.

## Capability Detection Patterns

NexusFlow uses pattern matching to detect required capabilities in user queries:

```python
# Information retrieval patterns
r"(find|research|search for|look up|get information on)",
r"(what is|who is|where is|when did)",

# Code generation patterns
r"(write|create|develop|implement|generate) (code|function|script|program|class)",
r"(debug|fix|solve) (code|error|bug)",

# Data analysis patterns
r"(analyze|analyse|examine|study) (data|dataset|numbers|statistics)",
r"(chart|graph|plot|visualize|visualisation|visualization)",

# Summarization patterns
r"(summarize|summarise|condense|shorten|digest)",
r"(give me the (highlights|key points|main ideas))",

# Planning patterns
r"(create a plan|plan for|steps to|how to accomplish)",
r"(break down|steps for|roadmap for)",

# Coordination patterns
r"(coordinate|manage|orchestrate|supervise)",
r"(combine results|synthesize findings)"
```

You can extend these patterns for custom capabilities to improve routing accuracy.

## Capability Dependencies

Some capabilities may depend on others. For example:

- **data_analysis** may depend on **reasoning**
- **coordination** may depend on **planning**
- **code_generation** may depend on **reasoning**

The capability registry can capture these dependencies to ensure agents have all the necessary capabilities.

```python
data_analysis_capability = Capability(
    type="data_analysis",
    name="Data Analysis",
    description="Ability to analyze data and generate insights",
    depends_on=["reasoning"]
)
```

## Capability-Based Flow Design

When designing flows, consider the following capability-based approaches:

### 1. Minimal Capability Set

Define the minimal set of capabilities needed for your flow:

```
research_flow = {
    core_capabilities: ["information_retrieval", "reasoning", "summarization"],
    optional_capabilities: ["data_analysis"]
}
```

### 2. Capability-Tool Mapping

Map capabilities to the tools they require:

```
capability_tool_map = {
    "information_retrieval": ["web_search", "document_retrieval"],
    "data_analysis": ["data_analysis", "code_execution"],
    "code_generation": ["code_execution"]
}
```

### 3. Capability-Based Agent Design

Design agents around capability clusters:

- **Research Agent**: information_retrieval + reasoning
- **Analysis Agent**: data_analysis + reasoning
- **Engineering Agent**: code_generation + reasoning
- **Content Agent**: summarization + reasoning
- **Coordination Agent**: coordination + planning + reasoning

## Best Practices

### Capability Assignment

1. **Be specific**: Assign only the capabilities an agent truly excels at
2. **Balance specialization**: Too specialized agents may be underutilized
3. **Consider overlaps**: Some capability overlap enables flexibility
4. **Match models to capabilities**: Use more powerful models for complex capabilities
5. **Consider tool requirements**: Ensure agents have the tools they need for their capabilities

### Capability System Messages

1. **Align with capabilities**: System messages should focus on the agent's capabilities
2. **Include capability-specific instructions**: Add specific guidelines for each capability
3. **Define boundaries**: Clarify what the agent should and shouldn't do
4. **Include examples**: Provide examples of good outputs for each capability
5. **Add decision guidelines**: Help agents make good delegation decisions

### Capability Debugging

If your flow isn't routing tasks correctly:

1. **Review capability assignments**: Ensure agents have appropriate capabilities
2. **Check capability detection**: Verify that input analysis is detecting the right capabilities
3. **Adjust capability scores**: Fine-tune scores to prioritize the best agents
4. **Examine system messages**: Make sure they align with the agent's capabilities
5. **Analyze execution traces**: Look for patterns in how tasks are being routed

## Common Capability Patterns

### Research and Analysis

```
User Query → Coordinator → Researcher → Analyst → Writer
```

Capabilities:
- **Coordinator**: coordination, planning, reasoning
- **Researcher**: information_retrieval, reasoning
- **Analyst**: data_analysis, reasoning
- **Writer**: summarization, reasoning

### Code Generation and Review

```
User Query → Planner → Coder → Reviewer → Explainer
```

Capabilities:
- **Planner**: planning, reasoning
- **Coder**: code_generation, reasoning
- **Reviewer**: code_generation, reasoning
- **Explainer**: summarization, reasoning

### Multi-Domain Specialist Team

```
                 ┌→ Research Specialist →┐
User Query → Coordinator →→ Medical Specialist →→ Writer
                 └→ Legal Specialist   →┘
```

Capabilities:
- **Coordinator**: coordination, planning, reasoning
- **Research Specialist**: information_retrieval, reasoning
- **Medical Specialist**: medical_diagnosis, reasoning
- **Legal Specialist**: legal_analysis, reasoning
- **Writer**: summarization, reasoning

## Advanced Capability Features

### Dynamic Capability Scoring

Adjust capability scores based on performance:

```python
def update_capability_score(agent_id, capability_type, performance_metric):
    current_score = capability_registry.get_agent_capability_score(agent_id, capability_type)
    new_score = current_score * 0.8 + performance_metric * 0.2  # Moving average
    capability_registry.update_agent_capability_score(agent_id, capability_type, new_score)
```

### Capability-Based Load Balancing

Distribute tasks among agents with the same capability:

```python
def get_agent_for_capability(capability_type):
    agents = capability_registry.get_agents_with_capability(capability_type)
    # Sort by score and load
    agents.sort(key=lambda a: a.score / (1 + a.current_load))
    return agents[0].agent_id
```

### Capability Versioning

Track capability versions for backward compatibility:

```python
data_analysis_v2 = Capability(
    type="data_analysis",
    name="Data Analysis",
    description="Enhanced ability to analyze data with advanced statistical methods",
    version="2.0",
    compatible_with=["1.0"]
)
```

## Monitoring Capability Performance

To optimize your capability assignments:

1. **Track success rates**: Monitor how well agents perform with each capability
2. **Measure delegation patterns**: Analyze how tasks flow between agents
3. **Identify gaps**: Look for capabilities that are frequently needed but underserved
4. **Evaluate agent utilization**: Check if some agents are overused or underused
5. **Monitor execution times**: Track how long each capability takes to execute

## Capability FAQ

### Q: How many capabilities should an agent have?

**A**: It depends on the agent's role:
- Specialist agents should have 1-2 primary capabilities
- Generalist agents might have 3-4 capabilities
- Coordinator agents often have coordination, planning, and reasoning capabilities

### Q: What happens if no agent has the required capability?

**A**: NexusFlow will fall back to agents with the reasoning capability, which serves as a default capability for handling miscellaneous tasks.

### Q: Can I create custom capabilities?

**A**: Yes, you can create custom capabilities by:
1. Defining the capability with a unique type
2. Registering it with the capability registry
3. Adding detection patterns for the capability
4. Assigning the capability to appropriate agents

### Q: How does capability scoring affect routing?

**A**: Higher capability scores increase the likelihood that an agent will be selected for tasks requiring that capability. This allows you to create primary and backup agents for specific capabilities.

### Q: Should I assign the reasoning capability to all agents?

**A**: Generally yes. The reasoning capability provides baseline problem-solving abilities that complement most other capabilities.

## Next Steps

After mastering capabilities, consider:

1. [Creating custom capabilities](custom_capabilities.md) for domain-specific tasks
2. [Optimizing capability assignments](capability_optimization.md) for better performance
3. [Implementing capability-based monitoring](capability_monitoring.md)
4. [Extending the capability detection system](capability_detection.md)
