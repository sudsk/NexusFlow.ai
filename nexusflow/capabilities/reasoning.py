"""
Reasoning Capability for NexusFlow.ai

This module implements the ReasoningCapability class, which represents
the general reasoning ability of agents in the NexusFlow system.
"""

from typing import Dict, List, Any, Optional, Set, Union
import logging
import re

from nexusflow.core.capability import Capability, CapabilityType

logger = logging.getLogger(__name__)

class ReasoningCapability(Capability):
    """
    Capability for general reasoning
    
    This capability enables agents to:
    - Analyze problems and questions
    - Break down complex issues into manageable parts
    - Apply logical thinking to derive conclusions
    - Explain thinking processes clearly
    - Make sound judgments based on available information
    """
    
    def __init__(self):
        """Initialize the reasoning capability"""
        super().__init__(
            type=CapabilityType.REASONING.value,
            name="General Reasoning",
            description="Ability to reason about general topics and answer questions",
            provides_output=["text", "explanation"],
            requires_input=["query"]
        )
        
        # Patterns that indicate reasoning needs
        self.reasoning_patterns = [
            r"why",
            r"how (does|do|can|could|would|should)",
            r"explain",
            r"reason",
            r"analyze",
            r"conclude",
            r"think about",
            r"what (is|are) the (reason|cause|effect|impact|result)",
            r"understand",
        ]
        
        # Example use cases
        self.examples = [
            {
                "name": "Problem analysis",
                "description": "Breaking down a complex problem into simpler components",
                "input": "Why are electric vehicles considered better for the environment than gas cars?",
                "output": "Electric vehicles are considered better for the environment than gas cars for several reasons:\n\n1. No direct emissions: EVs produce zero tailpipe emissions, reducing air pollution in urban areas.\n\n2. Overall efficiency: EVs convert about 77% of electrical energy to power, while gas cars only convert about 12-30% of fuel energy to power.\n\n3. Renewable energy potential: EVs can be powered by renewable electricity sources, further reducing their carbon footprint.\n\n4. Lower lifetime emissions: Studies show that even considering battery production, EVs typically have a lower lifetime carbon footprint.\n\nHowever, there are important considerations:\n- The electricity source matters (coal vs. renewable)\n- Battery production has environmental impacts\n- Battery recycling infrastructure needs improvement\n\nStill, most research indicates that EVs represent a net environmental benefit compared to conventional vehicles, especially as grids become cleaner."
            },
            {
                "name": "Conceptual explanation",
                "description": "Explaining complex concepts clearly",
                "input": "Explain how blockchain technology works.",
                "output": "Blockchain technology works as a decentralized digital ledger system that records transactions across multiple computers. Here's how it functions:\n\n1. Distributed ledger: Instead of a central database, information is stored across a network of computers (nodes).\n\n2. Blocks of data: Transactions are grouped into 'blocks' that contain:\n   - Transaction data\n   - Timestamp\n   - Cryptographic hash of the previous block\n\n3. Chain structure: Each block links to the previous one through its hash, creating a 'chain' of blocks.\n\n4. Consensus mechanisms: Nodes agree on the validity of transactions through protocols like:\n   - Proof of Work: Solving complex math problems (Bitcoin)\n   - Proof of Stake: Validators stake cryptocurrency (Ethereum 2.0)\n\n5. Immutability: Once recorded, data cannot be altered without changing all subsequent blocks and obtaining network consensus.\n\n6. Cryptographic security: Public and private keys secure transactions and verify ownership.\n\nThis structure creates a transparent, tamper-resistant record system without requiring a trusted central authority."
            }
        ]
    
    def matches_input(self, input_data: Dict[str, Any]) -> float:
        """
        Check if the input requires reasoning capability
        
        Args:
            input_data: Input data to analyze
            
        Returns:
            Match score between 0.0 and 1.0
        """
        query = input_data.get("query", "").lower()
        
        # Check if any reasoning patterns are present
        for pattern in self.reasoning_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return 0.8  # High match if reasoning indicators are present
        
        # Even without explicit reasoning patterns, most queries need some reasoning
        return 0.4  # Moderate default match
    
    def get_prompt_enhancement(self, input_data: Dict[str, Any]) -> str:
        """
        Get prompt enhancement for reasoning tasks
        
        Args:
            input_data: Input data for the task
            
        Returns:
            Prompt enhancement text
        """
        return """
Please approach this question using structured reasoning:

1. Identify the key elements of the question
2. Break down the problem into component parts
3. Consider multiple perspectives or approaches
4. Apply logical reasoning to each component
5. Synthesize your findings into a cohesive answer
6. Explain your thinking process clearly

Make sure your answer is:
- Well-structured and easy to follow
- Supported by logical arguments
- Complete and addresses all aspects of the question
- Balanced in considering different viewpoints
"""
    
    def get_system_message_guidance(self) -> str:
        """
        Get guidance for system message related to reasoning
        
        Returns:
            System message guidance
        """
        return """
You excel at reasoning and critical thinking. When responding:
- Break down complex questions into manageable components
- Approach problems step by step, showing your reasoning
- Consider multiple perspectives before drawing conclusions
- Identify assumptions and evaluate their validity
- Present logical, coherent arguments
- Acknowledge areas of uncertainty
- Provide explanations that are thorough yet concise
"""
