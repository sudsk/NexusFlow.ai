"""
Research Assistant Example

This example demonstrates a research assistant flow with multiple agents
collaborating based on their capabilities.
"""

import asyncio
import json
from typing import Dict, List, Any

from nexusflow.core.agent import Agent
from nexusflow.core.flow import Flow
from nexusflow.core.capability import CapabilityType

async def main():
    # Create tools
    web_search_tool = {
        "name": "web_search",
        "description": "Search the web for information on a topic",
        "parameters": {
            "query": {"type": "string", "description": "The search query"}
        },
        "handler": None  # In a real implementation, this would be a function
    }
    
    data_analysis_tool = {
        "name": "data_analysis",
        "description": "Analyze data using various techniques",
        "parameters": {
            "data": {"type": "string", "description": "Data to analyze"},
            "analysis_type": {"type": "string", "description": "Type of analysis to perform"}
        },
        "handler": None  # In a real implementation, this would be a function
    }
    
    # Create agents with different capabilities
    coordinator = Agent(
        name="Research Coordinator",
        description="Coordinates research efforts and synthesizes results",
        capabilities=[
            CapabilityType.COORDINATION.value,
            CapabilityType.PLANNING.value,
            CapabilityType.REASONING.value
        ],
        model_provider="openai",
        model_name="gpt-4",
        system_message="""You are a research coordinator who helps organize research efforts and synthesize findings.
Your job is to understand the research question, determine what information is needed, and coordinate with specialists.
At the end, you'll synthesize all the information into a comprehensive answer.""",
        temperature=0.3,
        can_delegate=True
    )
    
    researcher = Agent(
        name="Information Retriever",
        description="Retrieves information from the web",
        capabilities=[
            CapabilityType.INFORMATION_RETRIEVAL.value,
            CapabilityType.REASONING.value
        ],
        model_provider="openai",
        model_name="gpt-3.5-turbo",
        system_message="""You are an information retrieval specialist who finds factual information.
Your job is to search for accurate, relevant information on the given topic using web search.
Provide a concise summary of key facts and findings.""",
        temperature=0.3,
        tool_names=["web_search"],
        can_delegate=True
    )
    
    analyst = Agent(
        name="Data Analyst",
        description="Analyzes data and generates insights",
        capabilities=[
            CapabilityType.DATA_ANALYSIS.value,
            CapabilityType.REASONING.value
        ],
        model_provider="openai",
        model_name="gpt-4",
        system_message="""You are a data analyst who examines data and generates insights.
Your job is to analyze information, identify patterns, and draw meaningful conclusions.
Explain your findings clearly and support them with evidence.""",
        temperature=0.4,
        tool_names=["data_analysis"],
        can_delegate=True
    )
    
    writer = Agent(
        name="Content Writer",
        description="Writes clear, comprehensive content",
        capabilities=[
            CapabilityType.SUMMARIZATION.value,
            CapabilityType.REASONING.value
        ],
        model_provider="openai",
        model_name="gpt-4",
        system_message="""You are a content writer who creates clear, well-structured explanations.
Your job is to take research findings and present them in a comprehensive, easy-to-understand format.
Focus on clarity, logical flow, and engaging presentation.""",
        temperature=0.5,
        can_delegate=True
    )
    
    # Create tools dictionary
    tools = {
        "web_search": web_search_tool,
        "data_analysis": data_analysis_tool
    }
    
    # Create the flow
    flow = Flow(
        name="Research Assistant",
        description="A research assistant that helps answer complex questions",
        agents=[coordinator, researcher, analyst, writer],
        max_steps=10,
        tools=tools
    )
    
    # Run the flow with a research question
    input_data = {
        "query": "What are the environmental impacts of electric vehicles compared to traditional gasoline cars? Include information about battery production and electricity sources."
    }
    
    print(f"Executing flow with input: {input_data['query']}")
    print("---------------------------------------------------")
    
    result = await flow.execute(input_data)
    
    print("\nExecution complete!")
    print(f"Steps taken: {result.get('steps', 0)}")
    
    # Get the final output
    output = result.get("output", {})
    if hasattr(output, "to_dict"):
        output = output.to_dict()
    
    print("\nFinal output:")
    print("---------------------------------------------------")
    if "content" in output:
        print(output["content"])
    else:
        print(json.dumps(output, indent=2))
    
    print("\nExecution path:")
    print("---------------------------------------------------")
    for step in result.get("execution_trace", []):
        if "agent_name" in step:
            step_type = step.get("type", "unknown")
            if step_type == "agent_execution":
                print(f"{step.get('step', 0)}. {step['agent_name']} processed input")
            elif step_type == "delegation":
                print(f"{step.get('step', 0)}. {step['agent_name']} received delegation")
            elif step_type == "tool_execution":
                tool_name = step.get("decision", {}).get("tool_name", "unknown tool")
                print(f"{step.get('step', 0)}. {step['agent_name']} used {tool_name}")

if __name__ == "__main__":
    asyncio.run(main())
