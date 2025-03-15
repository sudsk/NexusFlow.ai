"""
Retrieval Capability for NexusFlow.ai

This module implements the RetrievalCapability class, which represents
the information retrieval ability of agents in the NexusFlow system.
"""

from typing import Dict, List, Any, Optional, Set, Union
import logging
import re

from nexusflow.core.capability import Capability, CapabilityType

logger = logging.getLogger(__name__)

class RetrievalCapability(Capability):
    """
    Capability for information retrieval
    
    This capability enables agents to:
    - Search for information from various sources
    - Retrieve relevant facts, data, and knowledge
    - Find up-to-date information on specific topics
    - Access external knowledge bases and search engines
    - Return properly cited information to questions
    """
    
    def __init__(self):
        """Initialize the retrieval capability"""
        super().__init__(
            type=CapabilityType.INFORMATION_RETRIEVAL.value,
            name="Information Retrieval",
            description="Ability to retrieve relevant information from external sources",
            requires_tools=["web_search", "document_retrieval"],
            provides_output=["information", "sources", "citations"],
            requires_input=["query"]
        )
        
        # Tool requirements
        self.required_tools = ["web_search"]
        self.optional_tools = ["document_retrieval", "knowledge_base", "academic_search"]
        
        # Patterns that indicate retrieval needs
        self.retrieval_patterns = [
            r"find (information|data|facts|details) (about|on|regarding)",
            r"search (for|about)",
            r"lookup",
            r"research",
            r"(what|who|where|when) (is|are|was|were)",
            r"latest (information|news|data|research) (about|on)",
            r"(tell|inform) me about",
            r"information on",
            r"facts (about|on|regarding)",
            r"(fetch|retrieve|get) (information|data|facts)"
        ]
        
        # Example use cases
        self.examples = [
            {
                "name": "Factual information search",
                "description": "Retrieving specific factual information",
                "input": "What is the population of Japan in 2023?",
                "output": "As of 2023, the population of Japan is approximately 125.7 million people.\n\nSource: World Bank Data, retrieved from web search."
            },
            {
                "name": "Research topic exploration",
                "description": "Finding information on a research topic",
                "input": "Research the impact of artificial intelligence on healthcare diagnostics.",
                "output": "# Impact of AI on Healthcare Diagnostics\n\nBased on my research, here are the key impacts of artificial intelligence on healthcare diagnostics:\n\n## Major Applications\n1. **Medical Imaging Analysis**\n   - AI algorithms can detect abnormalities in X-rays, MRIs, and CT scans with accuracy comparable to human radiologists\n   - Studies show AI can detect lung nodules, breast lesions, and brain hemorrhages with 90%+ accuracy\n\n2. **Pathology & Laboratory Tests**\n   - AI enhances microscopic analysis of tissue samples\n   - Reduces diagnostic errors by 85% when used as a second opinion system\n\n3. **Predictive Diagnostics**\n   - Identifies high-risk patients by analyzing patterns in electronic health records\n   - Can predict conditions like sepsis 6+ hours before traditional clinical recognition\n\n## Benefits\n- **Increased Accuracy**: Reduces diagnostic errors by 30-50% in specialized domains\n- **Speed**: Analyzes medical images or lab results in seconds versus minutes/hours\n- **Accessibility**: Brings expert-level diagnostics to underserved areas\n- **Cost Reduction**: Lowers healthcare costs by $16B annually through earlier detection\n\n## Challenges\n- **Regulatory Approval**: FDA has approved 80+ AI diagnostic tools, but regulatory frameworks are still evolving\n- **Integration Issues**: Legacy healthcare IT systems create implementation barriers\n- **Training Data Biases**: Algorithms may underperform for underrepresented populations\n\nSources:\n1. Journal of the American Medical Association (JAMA) - 2023 Special Issue on AI in Medicine\n2. Stanford Medicine's 2023 Report on AI in Healthcare\n3. World Health Organization's Guidelines on AI for Health"
            },
            {
                "name": "Current events query",
                "description": "Finding information about recent events",
                "input": "What were the major tech announcements from the most recent CES event?",
                "output": "Based on my search, here are the major tech announcements from the most recent Consumer Electronics Show (CES):\n\n# Major CES Tech Announcements\n\n## AI Integration\n- **AI PCs**: New laptop category with dedicated neural processing units (NPUs)\n- **AI Home Assistants**: Enhanced smart home systems with advanced contextual awareness\n- **Generative AI Tools**: Consumer applications for content creation and personalization\n\n## Display Technology\n- **Transparent OLED TVs**: LG unveiled a 77-inch transparent OLED display\n- **Micro LED Advancements**: Samsung showcased improved micro LED technology with better brightness\n- **Wireless OLED TVs**: Completely cordless TV solutions with wireless power transmission\n\n## Automotive Tech\n- **Software-Defined Vehicles**: Cars increasingly defined by software rather than hardware\n- **Advanced Driver Assistance**: Enhanced autonomous driving capabilities\n- **In-Car AI Experiences**: Personalized in-vehicle experiences powered by generative AI\n\n## Health Tech\n- **Non-Invasive Health Monitors**: Devices that track health metrics without skin contact\n- **AI Diagnostic Tools**: Consumer health devices with AI-powered insights\n- **Sleep Tech Innovations**: Advanced sleep tracking and improvement systems\n\nSources:\n- TechRadar CES Coverage\n- CNET CES Roundup\n- The Verge CES Special Report"
            }
        ]
    
    def matches_input(self, input_data: Dict[str, Any]) -> float:
        """
        Check if the input requires information retrieval capability
        
        Args:
            input_data: Input data to analyze
            
        Returns:
            Match score between 0.0 and 1.0
        """
        query = input_data.get("query", "").lower()
        
        # Check if any retrieval patterns are present
        for pattern in self.retrieval_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return 0.9  # High match if retrieval indicators are present
        
        # Check for specific question words that often indicate factual queries
        question_indicators = ["what", "who", "where", "when", "which", "how many", "how much"]
        if any(indicator in query for indicator in question_indicators):
            return 0.7  # Strong match for factual questions
        
        # Check if the query is about a specific topic that likely requires retrieval
        topic_indicators = [
            "history", "science", "politics", "technology", "company", "person", 
            "event", "product", "statistics", "data", "research", "study", "news"
        ]
        if any(indicator in query for indicator in topic_indicators):
            return 0.6  # Moderate-to-strong match for topic-based queries
        
        return 0.3  # Low default match
    
    def get_prompt_enhancement(self, input_data: Dict[str, Any]) -> str:
        """
        Get prompt enhancement for retrieval tasks
        
        Args:
            input_data: Input data for the task
            
        Returns:
            Prompt enhancement text
        """
        return """
To provide accurate and up-to-date information:

1. Search for relevant, reliable sources of information on this topic
2. Gather key facts, data, and details from authoritative sources
3. Verify information with multiple sources when possible
4. Organize the information in a clear, logical manner
5. Cite your sources to help establish credibility
6. Note any areas where information may be limited or uncertain

Focus on providing comprehensive, accurate information rather than speculation.
"""
    
    def get_system_message_guidance(self) -> str:
        """
        Get guidance for system message related to information retrieval
        
        Returns:
            System message guidance
        """
        return """
You excel at information retrieval. When responding:
- Actively search for accurate, relevant information from authoritative sources
- Use search tools effectively with well-crafted search queries
- Verify information across multiple sources when possible
- Present information in a structured, organized manner
- Cite sources to establish credibility
- Distinguish between verified facts and less certain information
- Acknowledge when information might be outdated or incomplete
"""
    
    def verify_agent_compatibility(self, agent_config: Dict[str, Any]) -> bool:
        """
        Check if an agent is compatible with this capability
        
        Args:
            agent_config: Agent configuration to check
            
        Returns:
            True if compatible, False otherwise
        """
        # Check if the agent has the necessary tools
        agent_tools = agent_config.get("tool_names", [])
        
        # Agent must have at least one required tool
        if not any(tool in agent_tools for tool in self.required_tools):
            return False
        
        return True
